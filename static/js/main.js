// نظام إدارة الإقرارات الضريبية - JavaScript الرئيسي

document.addEventListener('DOMContentLoaded', function() {
    // تهيئة التطبيق
    initializeApp();
    
    // تهيئة الرسوم البيانية
    initializeCharts();
    
    // تهيئة النماذج
    initializeForms();
    
    // تهيئة الجداول
    initializeTables();
});

// تهيئة التطبيق
function initializeApp() {
    // إضافة تأثيرات الحركة
    addAnimations();
    
    // تهيئة التنبيهات
    initializeAlerts();
    
    // تهيئة الشريط الجانبي
    initializeSidebar();
    
    // تهيئة البحث
    initializeSearch();
}

// إضافة تأثيرات الحركة
function addAnimations() {
    // تأثير fade-in للبطاقات
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // تأثير slide-in للشريط الجانبي
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.add('slide-in-right');
    }
}

// تهيئة التنبيهات
function initializeAlerts() {
    // إخفاء التنبيهات تلقائياً بعد 5 ثوان
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // إضافة زر إغلاق للتنبيهات
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'btn-close';
            closeBtn.setAttribute('aria-label', 'إغلاق');
            closeBtn.onclick = () => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            };
            alert.appendChild(closeBtn);
        }
    });
}

// تهيئة الشريط الجانبي
function initializeSidebar() {
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (toggleBtn && sidebar && mainContent) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
            
            // حفظ حالة الشريط الجانبي
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
        
        // استعادة حالة الشريط الجانبي
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('expanded');
        }
    }
}

// تهيئة البحث
function initializeSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value, this);
            }, 500);
        });
    });
}

// تنفيذ البحث
function performSearch(query, inputElement) {
    const searchForm = inputElement.closest('form');
    if (searchForm && query.length >= 2) {
        // إرسال البحث تلقائياً
        searchForm.submit();
    }
}

// تهيئة الرسوم البيانية
function initializeCharts() {
    // رسم بياني للمبيعات اليومية
    const dailySalesChart = document.getElementById('dailySalesChart');
    if (dailySalesChart) {
        createDailySalesChart();
    }
    
    // رسم بياني للضرائب
    const taxChart = document.getElementById('taxChart');
    if (taxChart) {
        createTaxChart();
    }
    
    // رسم بياني للمنتجات الأكثر مبيعاً
    const topProductsChart = document.getElementById('topProductsChart');
    if (topProductsChart) {
        createTopProductsChart();
    }
}

// إنشاء رسم بياني للمبيعات اليومية
function createDailySalesChart() {
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('dailySalesChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(item => new Date(item.date).toLocaleDateString('ar-EG')),
                    datasets: [{
                        label: 'المبيعات اليومية',
                        data: data.map(item => item.total_sales),
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                font: {
                                    family: 'Cairo'
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value.toLocaleString('ar-EG') + ' جنيه';
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('خطأ في تحميل بيانات المبيعات:', error));
}

// إنشاء رسم بياني للضرائب
function createTaxChart() {
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            const totalVAT = data.reduce((sum, item) => sum + item.vat_amount, 0);
            const totalWithholding = data.reduce((sum, item) => sum + item.withholding_amount, 0);
            
            const ctx = document.getElementById('taxChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['ضريبة القيمة المضافة', 'ضريبة الخصم والإضافة'],
                    datasets: [{
                        data: [totalVAT, totalWithholding],
                        backgroundColor: ['#3498db', '#e74c3c'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                font: {
                                    family: 'Cairo'
                                },
                                padding: 20
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('خطأ في تحميل بيانات الضرائب:', error));
}

// تهيئة النماذج
function initializeForms() {
    // تهيئة نماذج الفواتير
    initializeInvoiceForms();
    
    // تهيئة نماذج المنتجات
    initializeProductForms();
    
    // تهيئة التحقق من صحة النماذج
    initializeFormValidation();
    
    // تهيئة الحقول التلقائية
    initializeAutoFields();
}

// تهيئة نماذج الفواتير
function initializeInvoiceForms() {
    const productSelect = document.getElementById('product_id');
    const unitPriceInput = document.getElementById('unit_price');
    const quantityInput = document.getElementById('quantity');
    const discountInput = document.getElementById('discount_percentage');
    const totalDisplay = document.getElementById('line_total');
    
    if (productSelect && unitPriceInput) {
        productSelect.addEventListener('change', function() {
            if (this.value) {
                fetch(`/api/products/${this.value}`)
                    .then(response => response.json())
                    .then(data => {
                        unitPriceInput.value = data.price;
                        calculateLineTotal();
                    })
                    .catch(error => console.error('خطأ في تحميل بيانات المنتج:', error));
            }
        });
    }
    
    // حساب الإجمالي عند تغيير الكمية أو الخصم
    [quantityInput, discountInput, unitPriceInput].forEach(input => {
        if (input) {
            input.addEventListener('input', calculateLineTotal);
        }
    });
    
    function calculateLineTotal() {
        const quantity = parseFloat(quantityInput?.value || 0);
        const unitPrice = parseFloat(unitPriceInput?.value || 0);
        const discount = parseFloat(discountInput?.value || 0);
        
        const subtotal = quantity * unitPrice;
        const discountAmount = subtotal * (discount / 100);
        const total = subtotal - discountAmount;
        
        if (totalDisplay) {
            totalDisplay.textContent = total.toLocaleString('ar-EG', {
                style: 'currency',
                currency: 'EGP'
            });
        }
    }
}

// تهيئة نماذج المنتجات
function initializeProductForms() {
    const taxTypeSelect = document.getElementById('tax_type');
    const taxRateInput = document.getElementById('tax_rate');
    
    if (taxTypeSelect && taxRateInput) {
        taxTypeSelect.addEventListener('change', function() {
            if (this.value === 'vat') {
                taxRateInput.value = '14.0';
            } else if (this.value === 'withholding') {
                taxRateInput.value = '5.0';
            }
        });
    }
}

// تهيئة التحقق من صحة النماذج
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // إظهار رسائل الخطأ
                const invalidInputs = form.querySelectorAll(':invalid');
                invalidInputs.forEach(input => {
                    showFieldError(input);
                });
            }
            
            form.classList.add('was-validated');
        });
        
        // إزالة رسائل الخطأ عند التصحيح
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                if (this.checkValidity()) {
                    hideFieldError(this);
                }
            });
        });
    });
}

// إظهار خطأ الحقل
function showFieldError(input) {
    const errorDiv = input.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.style.display = 'block';
    }
    input.classList.add('is-invalid');
}

// إخفاء خطأ الحقل
function hideFieldError(input) {
    const errorDiv = input.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
}

// تهيئة الحقول التلقائية
function initializeAutoFields() {
    // تنسيق أرقام الهاتف
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.replace(/[^\d+\-\s]/g, '');
        });
    });
    
    // تنسيق الأرقام المالية
    const moneyInputs = document.querySelectorAll('input[step="0.01"]');
    moneyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    });
}

// تهيئة الجداول
function initializeTables() {
    // تهيئة الترتيب
    initializeTableSorting();
    
    // تهيئة الفلترة
    initializeTableFiltering();
    
    // تهيئة التحديد المتعدد
    initializeMultiSelect();
}

// تهيئة ترتيب الجداول
function initializeTableSorting() {
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    
    sortableHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const column = this.dataset.sort;
            const isAscending = !this.classList.contains('sort-asc');
            
            // إزالة فئات الترتيب من جميع العناوين
            sortableHeaders.forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
            });
            
            // إضافة فئة الترتيب الحالية
            this.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
            
            // ترتيب الصفوف
            rows.sort((a, b) => {
                const aValue = a.querySelector(`td[data-sort="${column}"]`)?.textContent || '';
                const bValue = b.querySelector(`td[data-sort="${column}"]`)?.textContent || '';
                
                const comparison = aValue.localeCompare(bValue, 'ar', { numeric: true });
                return isAscending ? comparison : -comparison;
            });
            
            // إعادة ترتيب الصفوف في الجدول
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

// تهيئة فلترة الجداول
function initializeTableFiltering() {
    const filterInputs = document.querySelectorAll('.table-filter');
    
    filterInputs.forEach(input => {
        input.addEventListener('input', function() {
            const table = document.querySelector(this.dataset.target);
            const filter = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    });
}

// تهيئة التحديد المتعدد
function initializeMultiSelect() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    
    if (selectAllCheckbox && itemCheckboxes.length > 0) {
        selectAllCheckbox.addEventListener('change', function() {
            itemCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBulkActions();
        });
        
        itemCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const checkedCount = document.querySelectorAll('.item-checkbox:checked').length;
                selectAllCheckbox.checked = checkedCount === itemCheckboxes.length;
                selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < itemCheckboxes.length;
                updateBulkActions();
            });
        });
    }
}

// تحديث إجراءات التحديد المتعدد
function updateBulkActions() {
    const checkedItems = document.querySelectorAll('.item-checkbox:checked');
    const bulkActions = document.querySelector('.bulk-actions');
    
    if (bulkActions) {
        bulkActions.style.display = checkedItems.length > 0 ? 'block' : 'none';
    }
}

// وظائف مساعدة
function showLoading(element) {
    element.classList.add('loading');
    element.disabled = true;
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} toast-notification`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        min-width: 300px;
        text-align: center;
        animation: slideDown 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideUp 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// تصدير الوظائف للاستخدام العام
window.TaxSystem = {
    showLoading,
    hideLoading,
    showToast,
    confirmAction
};
