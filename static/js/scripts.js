document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const resultSection = document.getElementById('result-section');
    const scanResult = document.getElementById('scan-result');
    const saveButton = document.getElementById('save-button');
    const receiptsList = document.getElementById('receipts-list');
    
    // Store the current receipt data
    let currentReceiptData = null;

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData();
        const fileField = document.getElementById('receipt-file');
        formData.append('file', fileField.files[0]);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            currentReceiptData = data.result; // Store the receipt data
            displayReceiptData(data.result);
            resultSection.style.display = 'block';
        })
        .catch(error => console.error('Error:', error));
    });

    function displayReceiptData(data) {
        let resultHtml = '<table class="receipt-table">';
        for (const [key, value] of Object.entries(data)) {
            resultHtml += `<tr><td><strong>${key}:</strong></td><td>${value}</td></tr>`;
        }
        resultHtml += '</table>';
        scanResult.innerHTML = resultHtml;
    }

    saveButton.addEventListener('click', function() {
        if (!currentReceiptData) {
            alert('No receipt data to save. Please scan a receipt first.');
            return;
        }

        fetch('/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentReceiptData)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            loadReceipts();
            // Clear the current receipt data after successful save
            currentReceiptData = null;
            resultSection.style.display = 'none';
            uploadForm.reset();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to save receipt. Please try again.');
        });
    });

    function loadReceipts() {
        fetch('/get_receipts')
        .then(response => response.json())
        .then(data => {
            receiptsList.innerHTML = '';
            for (const [month, receipts] of Object.entries(data)) {
                const monthElement = document.createElement('div');
                monthElement.className = 'month-section';
                monthElement.innerHTML = `<h4>${month}</h4>`;
                
                for (const [date, receipt] of Object.entries(receipts)) {
                    const receiptElement = document.createElement('div');
                    receiptElement.className = 'receipt-item';
                    let receiptHtml = `<div class="receipt-header">Date: ${new Date(date).toLocaleString()}</div>`;
                    receiptHtml += '<div class="receipt-details">';
                    for (const [key, value] of Object.entries(receipt)) {
                        receiptHtml += `<div><strong>${key}:</strong> ${value}</div>`;
                    }
                    receiptHtml += '</div>';
                    receiptElement.innerHTML = receiptHtml;
                    monthElement.appendChild(receiptElement);
                }
                receiptsList.appendChild(monthElement);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    loadReceipts();
});

