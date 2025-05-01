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

//     // تغيير لون الشريط الجانبي عند التمرير
// const sidebar = document.querySelector('.sidebar');

// if (sidebar) {
//     sidebar.addEventListener('mouseover', function () {
//         sidebar.style.transition = 'background-color 0.3s ease';
//         sidebar.style.backgroundColor = '#3a0ca3';  // لون عند التمرير
//     });

//     sidebar.addEventListener('mouseout', function () {
//         sidebar.style.transition = 'background-color 0.3s ease';
//         sidebar.style.backgroundColor = '#2d0b8a';  // اللون الأصلي
//     });
// }

// const links = document.querySelectorAll('.sidebar .nav-link');

// links.forEach(link => {
//     link.addEventListener('mouseenter', () => {
//         link.style.color = '#ffffff';
//         const icon = link.querySelector('i');
//         if (icon) icon.style.color = '#f0f0f0';
//     });

//     link.addEventListener('mouseleave', () => {
//         link.style.color = '#f0f0f0';
//         const icon = link.querySelector('i');
//         if (icon) icon.style.color = '#ffffff';
//     });
// });


// static/admin/custom.js
// document.addEventListener("DOMContentLoaded", function () {
//     document.querySelectorAll(".button-delete").forEach(button => {
//         button.addEventListener("click", function (event) {
//             event.preventDefault();
//             if (confirm("هل أنت متأكد أنك تريد حذف هذه المجموعة؟")) {
//                 window.location.href = this.getAttribute("href");
//             }
//         });
//     });
// });
// static/common/js/system_companies/custom.js
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
