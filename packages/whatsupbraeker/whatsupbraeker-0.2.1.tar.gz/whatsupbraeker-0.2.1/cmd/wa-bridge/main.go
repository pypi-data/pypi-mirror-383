package main

/*
#include <stdlib.h>
*/
import "C"

import (
	"context"
	"encoding/json"
	"errors"
	"strings"
	"time"
	"unsafe"

	"github.com/Alias1177/What-s-up-braeker/pkg/waclient"
	_ "github.com/mattn/go-sqlite3" // register SQLite driver
)

type Config struct {
	Phone           string `json:"phone"`
	Recipient       string `json:"recipient"`
	Message         string `json:"message"`
	DbURI           string `json:"db_uri"`
	Timeout         int    `json:"timeout"`
	ShowQR          bool   `json:"show_qr"`
	WaitForResponse bool   `json:"wait_for_response"`
	ConnectOnly     bool   `json:"connect_only"`
	ReceiveOnly     bool   `json:"receive_only"`
}

type Response struct {
	Success    bool      `json:"success"`
	MessageID  string    `json:"message_id,omitempty"`
	Messages   []Message `json:"messages,omitempty"`
	RequiresQR bool      `json:"requires_qr,omitempty"`
	Error      string    `json:"error,omitempty"`
}

type Message struct {
	ID        string `json:"id"`
	Timestamp int64  `json:"timestamp"`
	FromJID   string `json:"from_jid"`
	Text      string `json:"text"`
	IsGroup   bool   `json:"is_group"`
}

//export WaRun
func WaRun(configJSON *C.char) *C.char {
	raw := C.GoString(configJSON)

	config := Config{
		ShowQR:  true,
		Timeout: 30,
	}

	if err := json.Unmarshal([]byte(raw), &config); err != nil {
		return marshalResponse(Response{
			Error:   "invalid configuration JSON: " + err.Error(),
			Success: false,
		})
	}

	response := Response{Success: false}

	if config.Phone == "" {
		response.Error = "phone is required"
		return marshalResponse(response)
	}

	switch {
	case config.ConnectOnly:
		err := connectOnly(config)
		if err != nil {
			response.Error = err.Error()
			response.RequiresQR = isQRError(err)
		} else {
			response.Success = true
		}

	case config.ReceiveOnly:
		msgs, err := receiveMessages(config)
		if err != nil {
			response.Error = err.Error()
			response.RequiresQR = isQRError(err)
		} else {
			response.Success = true
			response.Messages = msgs
		}

	case config.Recipient != "" && config.Message != "":
		result, err := sendMessage(config)
		if err != nil {
			response.Error = err.Error()
			response.RequiresQR = isQRError(err)
		} else {
			response.Success = true
			response.MessageID = result.MessageID
			response.Messages = result.Messages
		}

	default:
		response.Error = "Invalid configuration: specify ConnectOnly, ReceiveOnly, or Recipient+Message"
	}

	return marshalResponse(response)
}

//export WaFree
func WaFree(ptr *C.char) {
	C.free(unsafe.Pointer(ptr))
}

func connectOnly(config Config) error {
	_, err := runClient(config, func(cfg *waclient.Config) {
		cfg.ConnectOnly = true
	})
	return err
}

func sendMessage(config Config) (*Response, error) {
	result, err := runClient(config, func(cfg *waclient.Config) {
		cfg.Message = config.Message
		cfg.Recipient = config.Recipient
		cfg.PhoneNumber = config.Recipient
		cfg.WaitForResponse = config.WaitForResponse
		if config.WaitForResponse && config.Timeout > 0 {
			timeout := time.Duration(config.Timeout) * time.Second
			cfg.ListenAfterSend = timeout
			cfg.ReceiveTimeout = timeout
		}
	})
	if err != nil {
		return nil, err
	}

	resp := &Response{
		MessageID: result.MessageID,
		Messages:  convertMessages(result.LastMessages),
	}
	return resp, nil
}

func receiveMessages(config Config) ([]Message, error) {
	result, err := runClient(config, func(cfg *waclient.Config) {
		cfg.ReceiveOnly = true
		if config.Timeout > 0 {
			cfg.ReceiveTimeout = time.Duration(config.Timeout) * time.Second
		}
	})
	if err != nil {
		return nil, err
	}
	return convertMessages(result.LastMessages), nil
}

type configMutator func(*waclient.Config)

func runClient(config Config, mutate configMutator, extra ...configMutator) (*waclient.Result, error) {
	ctx := context.Background()

	clientCfg := waclient.Config{
		DatabaseURI: config.DbURI,
		ShowQR:      config.ShowQR,
	}

	if config.Timeout > 0 {
		timeout := time.Duration(config.Timeout) * time.Second
		clientCfg.ReceiveTimeout = timeout
		clientCfg.ListenAfterSend = timeout
		clientCfg.QRTimeout = timeout
	}

	for _, fn := range append([]configMutator{mutate}, extra...) {
		if fn != nil {
			fn(&clientCfg)
		}
	}

	return waclient.Run(ctx, clientCfg)
}

func convertMessages(source []waclient.Message) []Message {
	if len(source) == 0 {
		return nil
	}

	out := make([]Message, 0, len(source))
	for _, msg := range source {
		out = append(out, Message{
			ID:        msg.ID,
			Timestamp: msg.Timestamp.Unix(),
			FromJID:   msg.FromJID,
			Text:      msg.Text,
			IsGroup:   msg.IsGroup,
		})
	}
	return out
}

func isQRError(err error) bool {
	if err == nil {
		return false
	}
	if errors.Is(err, waclient.ErrAuthenticationRequired) {
		return true
	}

	lower := strings.ToLower(err.Error())
	return strings.Contains(lower, "not logged in") ||
		strings.Contains(lower, "qr") ||
		strings.Contains(lower, "auth")
}

func marshalResponse(resp Response) *C.char {
	data, _ := json.Marshal(resp)
	return C.CString(string(data))
}

func main() {}
