document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        const connectionType = document.querySelector('#id_connection_type')?.value;
        const usernameField = document.querySelector('#id_username');
        const passwordField = document.querySelector('#id_password');

        // تحقق فقط إذا كان WiFi أو Serial وحقول المصادقة فاضية
        if ((connectionType === 'wifi' || connectionType === 'serial') &&
            (!usernameField.value || !passwordField.value)) {

            e.preventDefault();  // وقف الحفظ مؤقتًا

            const modal = document.createElement('div');
            modal.innerHTML = `
                <div style="position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center; z-index:9999;">
                    <div style="background:white; padding:20px; border-radius:8px; width:300px;">
                        <h3 style="margin-bottom:10px;">بيانات الاتصال مطلوبة</h3>
                        <label>اسم المستخدم</label>
                        <input id="modal_username" type="text" class="vTextField" style="width:100%; margin-bottom:10px;" />
                        <label>كلمة المرور</label>
                        <input id="modal_password" type="password" class="vTextField" style="width:100%; margin-bottom:15px;" />
                        <div style="text-align:right">
                            <button id="submit_modal" class="button default">تأكيد</button>
                            <button id="cancel_modal" class="button">إلغاء</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            document.getElementById('submit_modal').onclick = () => {
                const modalUsername = document.getElementById('modal_username').value;
                const modalPassword = document.getElementById('modal_password').value;

                if (!modalUsername || !modalPassword) {
                    alert("يرجى إدخال اسم المستخدم وكلمة المرور");
                    return;
                }

                // اكتبها في الحقول المخفية
                usernameField.value = modalUsername;
                passwordField.value = modalPassword;

                document.body.removeChild(modal);
                form.submit();  // أعد الإرسال
            };

            document.getElementById('cancel_modal').onclick = () => {
                document.body.removeChild(modal);
            };
        }
    });
});
