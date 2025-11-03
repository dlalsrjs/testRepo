document.addEventListener('DOMContentLoaded', function() {
    // URL에서 현재 모델과 객체 ID를 파악
    const pathArray = window.location.pathname.split('/').filter(Boolean);
    const modelName = pathArray[pathArray.length - 3]; // 예: 'japanesework'
    const objectId = pathArray[pathArray.length - 2];   // 'add' 또는 객체의 pk

    // 'urls'라는 이름의 필드를 찾음
    const urlField = document.querySelector('input[name="urls"]');

    if (urlField) {
        // 중복 결과를 표시할 div 생성
        const resultDiv = document.createElement('div');
        resultDiv.style.marginTop = '10px';
        resultDiv.style.padding = '10px';
        resultDiv.style.border = '1px solid #ccc';
        resultDiv.style.borderRadius = '4px';
        resultDiv.style.backgroundColor = '#f8f9fa';
        resultDiv.style.display = 'none'; // 처음에는 숨김
        urlField.parentNode.appendChild(resultDiv);

        let debounceTimer;

        urlField.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const urls = this.value.split(',')
                                     .map(url => url.trim())
                                     .filter(url => url);

                if (urls.length === 0) {
                    resultDiv.style.display = 'none';
                    return;
                }

                // 서버로 보낼 데이터 준비
                const data = {
                    urls: urls,
                    model_name: modelName,
                    current_id: objectId !== 'add' ? objectId : null
                };

                // 서버에 중복 검사 요청
                fetch('/videos/check-duplicate-url/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken') // CSRF 토큰 추가
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    resultDiv.style.display = 'block';
                    if (result.duplicates && result.duplicates.length > 0) {
                        resultDiv.style.borderColor = '#dc3545'; // 빨간색 테두리
                        resultDiv.style.color = '#dc3545';
                        let html = '<strong>⚠️ 중복된 URL이 존재합니다:</strong><ul>';
                        result.duplicates.forEach(url => {
                            html += `<li>${url}</li>`;
                        });
                        html += '</ul>';
                        resultDiv.innerHTML = html;
                    } else {
                        resultDiv.style.borderColor = '#28a745'; // 녹색 테두리
                        resultDiv.style.color = '#28a745';
                        resultDiv.innerHTML = '<strong>✅ 모든 URL이 고유합니다.</strong>';
                    }
                })
                .catch(error => {
                    console.error('URL 중복 검사 오류:', error);
                    resultDiv.style.display = 'block';
                    resultDiv.style.borderColor = '#ffc107';
                    resultDiv.style.color = '#212529';
                    resultDiv.innerHTML = 'URL 중복 검사 중 오류가 발생했습니다.';
                });
            }, 500); // 0.5초 디바운스
        });
    }

    // CSRF 토큰을 가져오는 함수
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});