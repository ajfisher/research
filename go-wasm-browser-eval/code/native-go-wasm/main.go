package main

import (
    "encoding/csv"
    "fmt"
    "strings"
    "syscall/js"
)

// summaryFromCSV returns the number of records and columns from a CSV payload.
// It is intentionally simple to mirror a subset of CLI-oriented processing in a browser.
func summaryFromCSV(csvText string) (map[string]any, error) {
    reader := csv.NewReader(strings.NewReader(csvText))
    rows, err := reader.ReadAll()
    if err != nil {
        return nil, fmt.Errorf("failed to parse csv: %w", err)
    }
    columnCount := 0
    if len(rows) > 0 {
        columnCount = len(rows[0])
    }
    return map[string]any{
        "rows":    len(rows),
        "columns": columnCount,
    }, nil
}

// wrapCSVSummary exposes summaryFromCSV to JavaScript.
func wrapCSVSummary(this js.Value, args []js.Value) any {
    if len(args) < 1 {
        return map[string]any{"error": "expected a CSV string"}
    }
    result, err := summaryFromCSV(args[0].String())
    if err != nil {
        return map[string]any{"error": err.Error()}
    }
    return result
}

// wrapUppercase exposes a basic string helper to demonstrate data flow between JS and Go.
func wrapUppercase(this js.Value, args []js.Value) any {
    if len(args) < 1 {
        return ""
    }
    return strings.ToUpper(args[0].String())
}

func main() {
    js.Global().Set("wasmCSVSummary", js.FuncOf(wrapCSVSummary))
    js.Global().Set("wasmUppercase", js.FuncOf(wrapUppercase))

    // Block forever so that exported functions remain available to JS.
    <-make(chan struct{})
}
