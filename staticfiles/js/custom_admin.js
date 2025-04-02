document.addEventListener("DOMContentLoaded", function () {
    let saveButton = document.querySelector('[name="_save"]'); // زر الحفظ في Django Admin

    saveButton.addEventListener("click", function (event) {
        let connectionType = document.querySelector("#id_connection_type").value;
        let usernameField = document.querySelector("#id_username");
        let passwordField = document.querySelector("#id_password");

        // تحقق مما إذا كان نوع الاتصال يتطلب تسجيل الدخول
        if ((connectionType === "wifi" || connectionType === "serial") && (!usernameField.value || !passwordField.value)) {
            event.preventDefault(); // منع الحفظ المباشر

            Swal.fire({
                title: "مطلوب بيانات تسجيل الدخول",
                text: "يرجى إدخال اسم المستخدم وكلمة المرور لهذا الجهاز.",
                icon: "warning",
                html: `
                    <input type="text" id="swal-username" class="swal2-input" placeholder="اسم المستخدم">
                    <input type="password" id="swal-password" class="swal2-input" placeholder="كلمة المرور">
                `,
                showCancelButton: true,
                confirmButtonText: "موافق",
                cancelButtonText: "إلغاء"
            }).then((result) => {
                if (result.isConfirmed) {
                    let enteredUsername = document.getElementById("swal-username").value;
                    let enteredPassword = document.getElementById("swal-password").value;

                    if (enteredUsername && enteredPassword) {
                        usernameField.value = enteredUsername;
                        passwordField.value = enteredPassword;
                        Swal.fire("تم الحفظ!", "الآن يمكنك الضغط على زر الحفظ مرة أخرى.", "success");
                    } else {
                        Swal.fire("خطأ", "يجب إدخال اسم المستخدم وكلمة المرور!", "error");
                    }
                }
            });
        }
    });
});
