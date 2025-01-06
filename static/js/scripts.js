document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const resultSection = document.getElementById('result-section');
    const scanResult = document.getElementById('scan-result');
    const saveButton = document.getElementById('save-button');
    const transactionsList = document.getElementById('transactions-list');
    const transactionType = document.getElementById('transaction-type');
    
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
            currentReceiptData = data.result;
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

        if (!transactionType.value) {
            alert('Please select a transaction type.');
            return;
        }

        // Ensure we have a valid amount
        let amount = currentReceiptData.Amount;
        if (amount === 'N/A' || amount === undefined) {
            amount = 0;
        }
        
        const transactionData = {
            ...currentReceiptData,
            Amount: amount,
            transaction_type: transactionType.value
        };

        fetch('/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(transactionData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            alert(data.message);
            loadTransactions();
            // Reset form
            currentReceiptData = null;
            resultSection.style.display = 'none';
            uploadForm.reset();
            transactionType.value = '';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to save transaction. Please try again.');
        });
    });

    function loadTransactions() {
        fetch('/get_transactions')
        .then(response => response.json())
        .then(data => {
            transactionsList.innerHTML = '';
            data.forEach(transaction => {
                const transactionElement = document.createElement('div');
                transactionElement.className = 'transaction-item';
                transactionElement.innerHTML = `
                    <div class="transaction-header">
                        <span class="transaction-type ${transaction.type}">${transaction.type}</span>
                        <span class="transaction-amount">₦${transaction.amount.toFixed(2)}</span>
                    </div>
                    <div class="transaction-date">${new Date(transaction.date).toLocaleString()}</div>
                    <div class="transaction-details">${JSON.stringify(transaction.details)}</div>
                `;
                transactionsList.appendChild(transactionElement);
            });
        })
        .catch(error => console.error('Error:', error));
    }

    loadTransactions();
});

