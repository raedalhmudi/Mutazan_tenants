document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded and parsed");

    // التحقق من أننا في الصفحة الصحيحة
    if (window.location.href.includes("/admin/system_companies/weightcard/")) {  
        console.log("On the correct page");

        // إضافة العداد
        let counterHTML = `
            <div style="background: black; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="color: red; font-size: 24px;">0</div>
                    <div>
                        <span style="color: white;">00:00:00</span><br>
                        <span style="color: white;">00/00/0000</span>
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

        // إنشاء عنصر للبوكسات
        let camerasHTML = `
            <div style="margin-bottom: 20px;">
                <!-- بوكس كاميرا الدخول -->
                <div class="card bg-dark" style="margin-bottom: 10px;">
                    <div class="card-header text-white" style="padding: 10px; font-size: 14px;">📷 بث كاميرا الدخول</div>
                    <div class="card-body text-center" style="padding: 10px;">
                        <img src="/video_feed/entry/" class="img-fluid" style="width: 100%; height: 150px; object-fit: cover;">
                    </div>
                </div>

                <!-- بوكس كاميرا الخروج -->
                <div class="card bg-dark" style="margin-bottom: 10px;">
                    <div class="card-header text-white" style="padding: 10px; font-size: 14px;">📷 بث كاميرا الخروج</div>
                    <div class="card-body text-center" style="padding: 10px;">
                        <img src="/video_feed/exit/" class="img-fluid" style="width: 100%; height: 150px; object-fit: cover;">
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
        } else {
            console.log("Save buttons container not found");
        }
    } else {
        console.log("Not on the correct page");
    }
});

    

// static/admin/custom.js
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".button-delete").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            if (confirm("هل أنت متأكد أنك تريد حذف هذه المجموعة؟")) {
                window.location.href = this.getAttribute("href");
            }
        });
    });
});
