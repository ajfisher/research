package main

import (
    "encoding/csv"
    "fmt"
    "strings"
    "syscall/js"
)

// csvOverview mirrors the native example but is compiled with TinyGo.
func csvOverview(csvText string) (map[string]any, error) {
    reader := csv.NewReader(strings.NewReader(csvText))
    rows, err := reader.ReadAll()
    if err != nil {
        return nil, fmt.Errorf("failed to parse csv: %w", err)
    }
    columns := 0
    if len(rows) > 0 {
        columns = len(rows[0])
    }
    return map[string]any{
        "rows":    len(rows),
        "columns": columns,
    }, nil
}

func exposeCSV(this js.Value, args []js.Value) any {
    if len(args) < 1 {
        return map[string]any{"error": "expected a CSV string"}
    }
    result, err := csvOverview(args[0].String())
    if err != nil {
        return map[string]any{"error": err.Error()}
    }
    return result
}

func exposeUpper(this js.Value, args []js.Value) any {
    if len(args) < 1 {
        return ""
    }
    return strings.ToUpper(args[0].String())
}

func main() {
    js.Global().Set("tinygoCSVOverview", js.FuncOf(exposeCSV))
    js.Global().Set("tinygoUpper", js.FuncOf(exposeUpper))
    select {} // keep running
}
