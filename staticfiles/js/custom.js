document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");  // تحديد نموذج الإدخال الأساسي
    if (!form) return;  // التأكد من وجود النموذج

    form.addEventListener("submit", function (event) {
        const connectionType = document.querySelector("#id_connection_type").value;  // معرفة نوع الاتصال

        if (connectionType === "wifi" || connectionType === "serial") {
            event.preventDefault();  // إيقاف عملية الحفظ مؤقتًا

            alert("⚠️ هذه الكاميرا تتطلب إدخال اسم المستخدم وكلمة المرور.");  // إظهار تنبيه للمستخدم

            let username = "";
            let password = "";

            while (!username) {
                username = prompt("أدخل اسم المستخدم للكاميرا:");
                if (!username) {
                    alert("⚠️ يجب إدخال اسم المستخدم!");
                }
            }

            while (!password) {
                password = prompt("أدخل كلمة المرور للكاميرا:");
                if (!password) {
                    alert("⚠️ يجب إدخال كلمة المرور!");
                }
            }

            if (username && password) {
                // إنشاء حقول مخفية لإرسال القيم إلى السيرفر
                let hiddenUsername = document.createElement("input");
                hiddenUsername.type = "hidden";
                hiddenUsername.name = "username";
                hiddenUsername.value = username;

                let hiddenPassword = document.createElement("input");
                hiddenPassword.type = "hidden";
                hiddenPassword.name = "password";
                hiddenPassword.value = password;

                form.appendChild(hiddenUsername);
                form.appendChild(hiddenPassword);

                form.submit();  // إكمال الحفظ بعد إدخال البيانات
            }
        }
    });
});
