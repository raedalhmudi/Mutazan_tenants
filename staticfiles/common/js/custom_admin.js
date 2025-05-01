// document.addEventListener("DOMContentLoaded", function () {
//     const saveBtn = document.querySelector("input[name='_save']");
//     const username = document.querySelector("#id_username");
//     const password = document.querySelector("#id_password");
//     const connectionType = document.querySelector("#id_connection_type");
//     const nameDevices = document.querySelector("#id_name_devices");

//     if (!saveBtn || !username || !password || !connectionType) return;

//     username.closest(".form-row").style.display = "none";
//     password.closest(".form-row").style.display = "none";

//     saveBtn.addEventListener("click", function (e) {
//         const connType = connectionType.value;
//         const deviceName = nameDevices.value;

//         // الأجهزة التي تتطلب مصادقة
//         const requiresAuthDevices = ['camera_1', 'camera_2', 'camera_3', 'camera_4'];

//         if ((connType === "wifi" || connType === "serial") &&
//             requiresAuthDevices.includes(deviceName) &&
//             (!username.value || !password.value)) {

//             e.preventDefault(); // منع الحفظ

//             Swal.fire({
//                 title: "🔐 أدخل اسم المستخدم وكلمة المرور",
//                 html:
//                     '<input id="swal-username" class="swal2-input" placeholder="اسم المستخدم">' +
//                     '<input id="swal-password" type="password" class="swal2-input" placeholder="كلمة المرور">',
//                 confirmButtonText: "متابعة",
//                 focusConfirm: false,
//                 preConfirm: () => {
//                     const u = document.getElementById("swal-username").value;
//                     const p = document.getElementById("swal-password").value;

//                     if (!u || !p) {
//                         Swal.showValidationMessage("يرجى تعبئة كل الحقول");
//                         return false;
//                     }

//                     username.value = u;
//                     password.value = p;

//                     setTimeout(() => saveBtn.click(), 100);
//                 }
//             });
//         }
//     });
// });
