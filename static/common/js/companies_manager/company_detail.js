//  // متغير لتحديد نوع التقرير الحالي
//     let currentReportType = 'daily';
    
//     document.addEventListener("DOMContentLoaded", function() {
//         // تعيين تاريخ اليوم كقيمة افتراضية
//         document.getElementById("daily-date").valueAsDate = new Date();
        
//         // تعيين نطاق أسبوعي افتراضي (من اليوم إلى بعد 7 أيام)
//         let today = new Date();
//         let nextWeek = new Date();
//         nextWeek.setDate(today.getDate() + 7);
        
//         document.getElementById("from-date").valueAsDate = today;
//         document.getElementById("to-date").valueAsDate = nextWeek;
//     });

//     document.getElementById("daily-report").addEventListener("click", function() {
//         currentReportType = 'daily';
//         document.getElementById("daily-fields").style.display = "block";
//         document.getElementById("weekly-fields").style.display = "none";
//         document.getElementById("monthly-fields").style.display = "none";
//     });
    
//     document.getElementById("weekly-report").addEventListener("click", function() {
//         currentReportType = 'weekly';
//         document.getElementById("daily-fields").style.display = "none";
//         document.getElementById("weekly-fields").style.display = "block";
//         document.getElementById("monthly-fields").style.display = "none";
//     });
    
//     document.getElementById("monthly-report").addEventListener("click", function() {
//         currentReportType = 'monthly';
//         document.getElementById("daily-fields").style.display = "none";
//         document.getElementById("weekly-fields").style.display = "none";
//         document.getElementById("monthly-fields").style.display = "block";
//     });
    
//     document.getElementById("print-report").addEventListener("click", function() {
//         let companyId = "{{ company.id }}";
//         let url = `/companies/${companyId}/print-weight-cards/`;
//         let params = [];
        
//         if (currentReportType === 'daily') {
//             let date = document.getElementById("daily-date").value;
//             params.push(`report_type=daily&date=${date}`);
//         } 
//         else if (currentReportType === 'weekly') {
//             let fromDate = document.getElementById("from-date").value;
//             let toDate = document.getElementById("to-date").value;
//             params.push(`report_type=weekly&from_date=${fromDate}&to_date=${toDate}`);
//         } 
//         else if (currentReportType === 'monthly') {
//             let month = document.getElementById("month-select").value;
//             let year = document.getElementById("year-select").value;
//             params.push(`report_type=monthly&month=${month}&year=${year}`);
//         }
        
//         window.open(`${url}?${params.join('&')}`, '_blank');
//     });

//     document.getElementById("fetch-data").addEventListener("click", function() {
//         let fetchStatus = document.getElementById("fetch-status");
//         fetchStatus.textContent = "⏳ جاري جلب البيانات...";
    
//         let companyId = "{{ company.id }}";
//         let params = [];
        
//         if (currentReportType === 'daily') {
//             let date = document.getElementById("daily-date").value;
//             params.push(`report_type=daily&date=${date}`);
//         } 
//         else if (currentReportType === 'weekly') {
//             let fromDate = document.getElementById("from-date").value;
//             let toDate = document.getElementById("to-date").value;
//             params.push(`report_type=weekly&from_date=${fromDate}&to_date=${toDate}`);
//         } 
//         else if (currentReportType === 'monthly') {
//             let month = document.getElementById("month-select").value;
//             let year = document.getElementById("year-select").value;
//             params.push(`report_type=monthly&month=${month}&year=${year}`);
//         }
    
//         fetch(`/companies/${companyId}/fetch-data/?${params.join('&')}`)
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === "success") {
//                 fetchStatus.textContent = "✅ تم جلب البيانات بنجاح!";
                
//                 let tableBody = document.getElementById("table-body");
//                 tableBody.innerHTML = "";
//                 data.cards.forEach(card => {
//                     let row = `
//                         <tr>
//                             <td>${card.plate_number}</td>
//                             <td>${card.empty_weight}</td>
//                             <td>${card.loaded_weight}</td>
//                             <td>${card.net_weight}</td>
//                             <td>${card.driver_name}</td>
//                             <td>${card.entry_date}</td>
//                             <td>${card.exit_date}</td>
//                             <td>${card.material}</td>
//                             <td>${card.status}</td>
//                         </tr>
//                     `;
//                     tableBody.innerHTML += row;
//                 });
//             } else {
//                 fetchStatus.textContent = "❌ فشل في جلب البيانات!";
//             }
//         })
//         .catch(error => {
//             fetchStatus.textContent = "❌ خطأ في الاتصال!";
//             console.error(error);
//         });
//     });
