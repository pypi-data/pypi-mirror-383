package waclient

import (
	"context"
	"errors"
	"fmt"
	"io"
	"os"
	"sync"
	"time"

	"github.com/mdp/qrterminal/v3"
	"go.mau.fi/whatsmeow"
	waProto "go.mau.fi/whatsmeow/binary/proto"
	"go.mau.fi/whatsmeow/store/sqlstore"
	"go.mau.fi/whatsmeow/types"
	"go.mau.fi/whatsmeow/types/events"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/protobuf/proto"
)

var (
	defaultWaitBeforeSend = 5 * time.Second
	defaultReceiveTimeout = 10 * time.Second
	defaultQRTimeout      = 60 * time.Second

	// ErrAuthenticationRequired signals that the client must be authenticated via QR code.
	ErrAuthenticationRequired = errors.New("authentication required: scan QR code")
)

// Message describes a message observed during the client session.
type Message struct {
	ID        string
	Timestamp time.Time
	FromJID   string
	Text      string
	IsGroup   bool
}

// Result holds information gathered during the client session.
type Result struct {
	LastMessages []Message
	MessageID    string
	RequiresQR   bool
}

// Config contains parameters used to run the WhatsApp client.
type Config struct {
	DatabaseURI       string
	PhoneNumber       string
	Recipient         string
	Message           string
	WaitBeforeSend    time.Duration
	ListenAfterSend   time.Duration
	ReceiveTimeout    time.Duration
	QRTimeout         time.Duration
	Output            io.Writer
	QRWriter          io.Writer
	LogLevel          string
	LogEnableColor    bool
	DisableQRPrinting bool
	ConnectOnly       bool
	ReceiveOnly       bool
	WaitForResponse   bool
	ShowQR            bool
}

// Run spins up the WhatsApp client according to the supplied configuration.
func Run(ctx context.Context, cfg Config) (*Result, error) {
	cfg = normalizeConfig(cfg)

	log := waLog.Stdout("Client", cfg.LogLevel, cfg.LogEnableColor)

	container, err := sqlstore.New(ctx, "sqlite3", cfg.DatabaseURI, log)
	if err != nil {
		return nil, fmt.Errorf("init store: %w", err)
	}
	defer container.Close()

	deviceStore, err := container.GetFirstDevice(ctx)
	if err != nil {
		return nil, fmt.Errorf("get device: %w", err)
	}

	client := whatsmeow.NewClient(deviceStore, log)

	var (
		messagesMu   sync.Mutex
		outputMu     sync.Mutex
		lastMessages []Message
	)

	println := func(format string, args ...interface{}) {
		outputMu.Lock()
		defer outputMu.Unlock()
		fmt.Fprintf(cfg.Output, format+"\n", args...)
	}

	client.AddEventHandler(func(evt interface{}) {
		switch v := evt.(type) {
		case *events.Message:
			text := v.Message.GetConversation()
			if text == "" && v.Message.ExtendedTextMessage != nil {
				text = v.Message.ExtendedTextMessage.GetText()
			}
			if text == "" {
				return
			}

			from := v.Info.Chat.String()
			if v.Info.Sender.User != "" {
				from = v.Info.Sender.String()
			}

			msg := Message{
				ID:        v.Info.ID,
				Timestamp: v.Info.Timestamp,
				FromJID:   from,
				Text:      text,
				IsGroup:   v.Info.IsGroup,
			}

			messagesMu.Lock()
			lastMessages = append(lastMessages, msg)
			messagesMu.Unlock()

			println("📩 Новое сообщение от %s: %s", from, text)

		case *events.HistorySync:
			println("📚 Получена история чатов")
		}
	})

	result := &Result{}
	connected := false

	if client.Store.ID == nil {
		result.RequiresQR = true
		println("Отсканируй QR-код в WhatsApp для авторизации.")

		ok, err := handleLogin(ctx, client, cfg, println)
		if err != nil {
			return result, err
		}
		if !ok {
			return result, ErrAuthenticationRequired
		}
		connected = true
		result.RequiresQR = false
		println("✅ Авторизация выполнена.")
	} else {
		if err := client.Connect(); err != nil {
			return result, fmt.Errorf("connect: %w", err)
		}
		connected = true
		println("✅ Подключено к WhatsApp!")
	}

	defer func() {
		if connected {
			client.Disconnect()
		}
	}()

	if cfg.ConnectOnly {
		println("✨ Режим подключения завершён.")
		return result, nil
	}

	if cfg.ReceiveOnly {
		if cfg.WaitBeforeSend > 0 {
			println("⏳ Жду стабилизации соединения %d секунд...", int(cfg.WaitBeforeSend.Seconds()))
			waitFor(ctx, cfg.WaitBeforeSend)
		}

		if cfg.ReceiveTimeout > 0 {
			println("👂 Слушаю входящие сообщения %d секунд...", int(cfg.ReceiveTimeout.Seconds()))
			waitFor(ctx, cfg.ReceiveTimeout)
		}

		messagesMu.Lock()
		result.LastMessages = append([]Message(nil), lastMessages...)
		messagesMu.Unlock()

		println("🔌 Отключаюсь после прослушивания.")
		return result, nil
	}

	if cfg.Message == "" {
		return result, fmt.Errorf("message is required for send mode")
	}

	if cfg.Recipient == "" {
		return result, fmt.Errorf("recipient phone number is required")
	}

	if cfg.WaitBeforeSend > 0 {
		println("⏳ Жду стабилизации соединения %d секунд...", int(cfg.WaitBeforeSend.Seconds()))
		waitFor(ctx, cfg.WaitBeforeSend)
	}

	println("📤 Отправляю сообщение получателю %s", cfg.Recipient)
	msgResp, err := client.SendMessage(ctx, types.NewJID(cfg.Recipient, types.DefaultUserServer), &waProto.Message{
		Conversation: proto.String(cfg.Message),
	})
	if err != nil {
		return result, fmt.Errorf("send message: %w", err)
	}

	result.MessageID = msgResp.ID
	println("✅ Сообщение отправлено! ID: %s", msgResp.ID)

	if cfg.WaitForResponse {
		listen := cfg.ListenAfterSend
		if listen <= 0 {
			listen = cfg.ReceiveTimeout
		}

		if listen > 0 {
			println("👂 Слушаю ответы %d секунд...", int(listen.Seconds()))
			waitFor(ctx, listen)

			messagesMu.Lock()
			result.LastMessages = append([]Message(nil), lastMessages...)
			messagesMu.Unlock()
		}
	}

	println("🔌 Отключаюсь...")
	return result, nil
}

func normalizeConfig(cfg Config) Config {
	if cfg.DatabaseURI == "" {
		cfg.DatabaseURI = "file:whatsapp.db?_foreign_keys=on"
	}
	if cfg.Output == nil {
		cfg.Output = os.Stdout
	}
	if cfg.QRWriter == nil {
		cfg.QRWriter = cfg.Output
	}
	if cfg.WaitBeforeSend <= 0 {
		cfg.WaitBeforeSend = defaultWaitBeforeSend
	}
	if cfg.ListenAfterSend < 0 {
		cfg.ListenAfterSend = 0
	}
	if cfg.ReceiveTimeout <= 0 {
		cfg.ReceiveTimeout = defaultReceiveTimeout
	}
	if cfg.QRTimeout <= 0 {
		cfg.QRTimeout = defaultQRTimeout
	}
	if cfg.LogLevel == "" {
		cfg.LogLevel = "INFO"
	}
	if cfg.ShowQR {
		cfg.DisableQRPrinting = false
	} else {
		cfg.DisableQRPrinting = true
	}
	if cfg.Recipient == "" {
		cfg.Recipient = cfg.PhoneNumber
	}
	return cfg
}

func handleLogin(ctx context.Context, client *whatsmeow.Client, cfg Config, println func(string, ...interface{})) (bool, error) {
	qrChan, err := client.GetQRChannel(ctx)
	if err != nil {
		return false, fmt.Errorf("get qr channel: %w", err)
	}

	if err := client.Connect(); err != nil {
		return false, fmt.Errorf("connect (qr): %w", err)
	}

	timer := time.NewTimer(cfg.QRTimeout)
	defer timer.Stop()

	for {
		select {
		case evt, ok := <-qrChan:
			if !ok {
				return true, nil
			}

			switch evt.Event {
			case "code":
				if !cfg.DisableQRPrinting {
					qrterminal.GenerateHalfBlock(evt.Code, qrterminal.L, cfg.QRWriter)
				}
				println("QR-код обновлён, отсканируй его в WhatsApp.")

			case "success":
				println("Авторизация прошла успешно.")
				return true, nil

			case "timeout":
				println("Истекло время действия QR-кода, попробуй снова.")
				client.Disconnect()
				return false, ErrAuthenticationRequired

			default:
				println("Событие QR: %s", evt.Event)
			}

		case <-timer.C:
			println("Истекло время ожидания авторизации.")
			client.Disconnect()
			return false, ErrAuthenticationRequired

		case <-ctx.Done():
			client.Disconnect()
			return false, ctx.Err()
		}
	}
}

func waitFor(ctx context.Context, d time.Duration) {
	if d <= 0 {
		return
	}

	timer := time.NewTimer(d)
	defer timer.Stop()

	select {
	case <-timer.C:
	case <-ctx.Done():
	}
}
