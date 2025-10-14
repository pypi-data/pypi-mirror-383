from typing import List, Dict

def _map_typedef_name(reg_name: str) -> str:
    """
    'DENALI_CTL_00' -> 'stCTL00'
    규칙: 'DENALI_' 접두 제거 후 남은 토큰을 붙여 타입명으로 사용, 앞에 'st' 접두
    """
    parts = reg_name.split("_")
    if len(parts) >= 3 and parts[0] == "DENALI":
        core = parts[1] + parts[2]  # CTL + 00 -> CTL00
    else:
        core = reg_name.replace("_", "")
    return f"st{core}"

def _insert_reserved(fields_sorted: List[Dict]) -> List[Dict]:
    """
    LSB 오름차순 정렬된 필드 목록(각 항목: {'fieldName','lsb','bitWidth','description'})
    사이 갭을 RSVDn으로 채워 0..31 총 32비트가 되도록 반환
    """
    out = []
    cursor = 0
    rsvd_idx = 0
    for f in fields_sorted:
        lsb = int(f["lsb"])
        width = int(f["bitWidth"])
        if lsb > cursor:
            out.append({
                "fieldName": f"RSVD{rsvd_idx}",
                "lsb": cursor,
                "bitWidth": lsb - cursor,
                "description": "Reserved"
            })
            rsvd_idx += 1
        out.append(f)
        cursor = lsb + width
    if cursor < 32:
        out.append({
            "fieldName": f"RSVD{rsvd_idx}",
            "lsb": cursor,
            "bitWidth": 32 - cursor,
            "description": "Reserved"
        })
    return out

def build_c_code_from_json(json_data):
    """
    기대 JSON 스키마 (필수: lsb 포함, LSB=0 기준):
    [
      {
        "registerName": "DENALI_CTL_00",
        "structName": "ST_DENALI_CTL_00",   # 있으면 사용, 없으면 생성
        "fields": [
          {"fieldName":"START", "lsb":0, "bitWidth":1, "description":"Start initialization"},
          {"fieldName":"DRAM_CLASS", "lsb":8, "bitWidth":4, "description":"DRAM type/class"},
          {"fieldName":"CONTROLLER_ID", "lsb":16, "bitWidth":16, "description":"Controller ID"}
        ]
      },
      ...
    ]
    """
    output_units = []

    for reg in json_data:
        reg_name = reg["registerName"]
        struct_tag = reg.get("structName") or f"ST_{reg_name}"
        typedef_name = _map_typedef_name(reg_name)

        fields = reg["fields"]
        # 1) LSB 기준 정렬
        fields_sorted = sorted(fields, key=lambda x: int(x["lsb"]))
        # 2) RSVD 채우기
        fields_filled = _insert_reserved(fields_sorted)

        # 3) C 코드 생성 (LSB -> MSB 순서로 비트필드 선언)
        lines = [
            f"/** {reg_name} register definition */",
            f"typedef struct _{struct_tag}_ {{",
            "    union {",
            "        uint32_t value;  /**< full 32-bit register value */",
            "        struct {"
        ]
        for f in fields_filled:
            lines.append(
                f"            uint32_t {f['fieldName']} : {int(f['bitWidth'])};  /**< {f['description']} */"
            )
        lines += ["        };", "    };", f"}} {typedef_name};\n"]

        output_units.append("\n".join(lines))

    return "\n".join(output_units)

# Gemini에게 요구할 스키마 (lsb 추가!)
CODE_GEN_SCHEMA = {
    "type": "ARRAY",
    "items": {
        "type": "OBJECT",
        "properties": {
            "registerName": {"type": "STRING"},
            "structName": {"type": "STRING"},
            "fields": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "fieldName": {"type": "STRING"},
                        "lsb": {"type": "INTEGER"},          # <= 추가됨
                        "bitWidth": {"type": "INTEGER"},
                        "description": {"type": "STRING"}
                    },
                    "required": ["fieldName", "lsb", "bitWidth", "description"]
                }
            }
        },
        "required": ["registerName", "fields"]
    }
}
