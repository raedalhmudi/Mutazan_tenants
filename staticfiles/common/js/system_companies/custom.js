document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded and parsed");

    // التحقق من أننا في الصفحة الصحيحة
    if (window.location.href.includes("/admin/system_companies/weightcard/add")) {  
        console.log("On the correct page");

        // إضافة العداد
        let counterHTML = `
            <div style="
                background: linear-gradient(135deg, #4a6682, #3a5470);
                padding: 15px;
                border-radius: 12px;
                text-align: center;
                margin-bottom: 25px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                color: white;
                font-family: 'Segoe UI', sans-serif;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="
                        color: #fff;
                        font-size: 24px;
                        font-weight: 600;
                        background: rgba(0,0,0,0.2);
                        padding: 8px 15px;
                        border-radius: 8px;
                    ">0</div>
                    <div>
                        <span style="
                            font-size: 18px;
                            font-weight: 500;
                            display: block;
                            margin-bottom: 5px;
                        ">00:00:00</span>
                        <span style="
                            font-size: 14px;
                            opacity: 0.9;
                        ">00/00/0000</span>
                    </div>
                </div>
            </div>
        `;

        // إضافة العداد فوق الفورم
        let formContainer = document.querySelector(".content form");
        if (formContainer) {
            formContainer.insertAdjacentHTML("beforebegin", counterHTML);
            console.log("Counter added");
        }

        // إنشاء عنصر للبوكسات بتصميم عصري وترتيب عمودي
        let camerasHTML = `
            <div style="
                margin-bottom: 30px;
                display: flex;
                flex-direction: column;
                gap: 20px;
            ">
                <!-- بوكس كاميرا الدخول -->
                <div class="camera-card" style="
                    background: #fff;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    overflow: hidden;
                    transition: all 0.3s ease;
                    border: 1px solid #f1f1f1;
                ">
                    <div class="camera-header" style="
                        background: linear-gradient(135deg, #4a6682, #3a5470);
                        color: white;
                        padding: 12px 15px;
                        font-size: 14px;
                        font-weight: 600;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    ">
                        <i class="fas fa-sign-in-alt" style="font-size: 16px;"></i>
                        <span>بث كاميرا الدخول</span>
                    </div>
                    <div class="camera-feed" style="
                        padding: 10px;
                        background: #f9f9f9;
                        text-align: center;
                        height: 250px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        <img src="/video_feed/entry/" class="img-fluid" style="
                            width: 100%;
                            height: 100%;
                            object-fit: cover;
                            border-radius: 6px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        ">
                    </div>
                </div>

                <!-- بوكس كاميرا الخروج -->
                <div class="camera-card" style="
                    background: #fff;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    overflow: hidden;
                    transition: all 0.3s ease;
                    border: 1px solid #f1f1f1;
                ">
                    <div class="camera-header" style="
                        background: linear-gradient(135deg, #4a6682, #3a5470);
                        color: white;
                        padding: 12px 15px;
                        font-size: 14px;
                        font-weight: 600;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    ">
                        <i class="fas fa-sign-out-alt" style="font-size: 16px;"></i>
                        <span>بث كاميرا الخروج</span>
                    </div>
                    <div class="camera-feed" style="
                        padding: 10px;
                        background: #f9f9f9;
                        text-align: center;
                        height: 250px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        <img src="/video_feed/exit/" class="img-fluid" style="
                            width: 100%;
                            height: 100%;
                            object-fit: cover;
                            border-radius: 6px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        ">
                    </div>
                </div>
            </div>
        `;

        // البحث عن أزرار الحفظ
        let saveButtonsContainer = document.querySelector("#jazzy-actions");
        if (saveButtonsContainer) {
            console.log("Save buttons container found");

            // إضافة البوكسات فوق أزرار الحفظ
            saveButtonsContainer.insertAdjacentHTML("beforebegin", camerasHTML);
            console.log("Cameras added above save buttons");
            
            // إضافة تأثيرات hover للكاميرات
            document.querySelectorAll('.camera-card').forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-5px)';
                    this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = '';
                    this.style.boxShadow = '0 4px 20px rgba(0,0,0,0.08)';
                });
            });
        } else {
            console.log("Save buttons container not found");
        }
    } else {
        console.log("Not on the correct page");
    }
});

document.addEventListener("DOMContentLoaded", function () {
    // التأكد أننا في صفحة بطاقات الوزن
    if (window.location.pathname.includes("/admin/system_companies/weightcard")) {
        const pageHeader = document.querySelector("h1");

        if (pageHeader && pageHeader.textContent.includes("بطاقات الوزن")) {
            // تحقق من عدم تكرار الأيقونة
            if (!pageHeader.innerHTML.includes("fa-balance-scale-left")) {
                pageHeader.innerHTML = `<i class="fas fa-balance-scale-left" style="margin-left: 10px; color :rgb(74, 102, 130)"></i> ${pageHeader.textContent.trim()}`;
            }
        }
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const fullscreenButton = document.getElementById("fullscreen-button");
    if (fullscreenButton) {
        fullscreenButton.addEventListener("click", function (e) {
            e.preventDefault();
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        });
    }
});
