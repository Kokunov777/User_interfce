import re


def analyze_text(language: str, text: str) -> list[tuple[int, int, str]]:
    if language == "python":
        return _analyze_python(text)
    return _analyze_c_like(language, text)


def _analyze_python(text: str) -> list[tuple[int, int, str]]:
    try:
        compile(text, "<editor>", "exec")
        return []
    except SyntaxError as error:
        line = error.lineno or 1
        col = error.offset or 1
        return [(line, col, error.msg or "Syntax error")]


def _analyze_c_like(language: str, text: str) -> list[tuple[int, int, str]]:
    errors: list[tuple[int, int, str]] = []
    types_map = {
        "c": {"int", "float", "double", "char", "long", "short", "void", "bool"},
        "c++": {"int", "float", "double", "char", "long", "short", "void", "bool", "auto", "string"},
        "c#": {"int", "float", "double", "char", "long", "short", "void", "bool", "string", "var", "decimal"},
        "rust": {"i8", "i16", "i32", "i64", "u8", "u16", "u32", "u64", "f32", "f64", "bool", "char", "String", "usize"},
    }
    known_types = types_map.get(language, set())

    for i, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("//") or line in {"{", "}"}:
            continue

        if not line.endswith(";") and not line.endswith("{") and not line.endswith("}"):
            errors.append((i, len(raw_line), "Отсутствует ';' в конце оператора"))

        tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\S", line)
        if not tokens:
            continue

        if tokens[0] in known_types:
            if len(tokens) < 2:
                errors.append((i, 1, "Отсутствует идентификатор после типа"))
                continue
            ident = tokens[1]
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", ident):
                col = max(1, raw_line.find(ident) + 1)
                errors.append((i, col, f"Неверный идентификатор '{ident}'"))
            if len(tokens) > 2 and tokens[2] not in {"=", ";"}:
                col = max(1, raw_line.find(tokens[2]) + 1)
                errors.append((i, col, "Неверное задание константы"))

        bad_number_ident = re.search(r"\b\d+[A-Za-z_]+\w*\b", line)
        if bad_number_ident:
            errors.append((i, bad_number_ident.start() + 1, "Неверное задание константы"))

    return errors
