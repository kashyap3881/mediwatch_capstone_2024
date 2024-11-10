// Initialize all collapse buttons
document.querySelectorAll('.collapse-btn').forEach(button => {
    // Set initial state to open
    button.classList.add('active');
    const content = button.nextElementSibling;
    content.style.maxHeight = content.scrollHeight + "px";

    // Add click handler
    button.addEventListener('click', () => {
        button.classList.toggle('active');
        const content = button.nextElementSibling;
        
        if (button.classList.contains('active')) {
            content.style.maxHeight = content.scrollHeight + "px";
        } else {
            content.style.maxHeight = null;
        }
    });
});


$(document).ready(function() {
    let fileContent = '';
    let chart = null;

    function createTableFromCSV(csv) {
        const rows = csv.split('\n');
        const headers = rows[0].split(',');
        let tableHtml = '<table><thead><tr>';
        
        headers.forEach(header => {
            tableHtml += `<th>${header}</th>`;
        });
        
        tableHtml += '</tr></thead><tbody>';
        
        for (let i = 1; i < Math.min(rows.length, 100); i++) {
            const cells = rows[i].split(',');
            tableHtml += '<tr>';
            cells.forEach(cell => {
                tableHtml += `<td>${cell}</td>`;
            });
            tableHtml += '</tr>';
        }
        
        tableHtml += '</tbody></table>';
        return tableHtml;
    }

    $('#csvFile').change(function(e) {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            fileContent = e.target.result;
            const tableHtml = createTableFromCSV(fileContent);
            $('#csvPreviewTable').html(tableHtml);
        };
        reader.readAsText(file);
    });

    $('#predictBtn').click(function() {
        if (!fileContent) {
            alert('Please upload a CSV file first.');
            return;
        }

        $.ajax({
            url: '/predict',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({csv: btoa(fileContent)}),
            success: function(response) {
                const data = response["Hospital Readmission Prediction"];
                const times = data.map(item => item.patient_id);
                const threads = data.map(item => item.readmitted);
                const predictedThreads = data.map(item => item.predicted_readmitted);

                if (chart) {
                    chart.destroy();
                }

                chart = new Chart($('#predictionChart'), {
                    type: 'line',
                    data: {
                        labels: times,
                        datasets: [{
                            label: 'Actual Readmission Status',
                            data: threads,
                            borderColor: 'blue',
                            fill: false
                        }, {
                            label: 'Predicted Readmission Status',
                            data: predictedThreads,
                            borderColor: 'red',
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        title: {
                            display: true,
                            text: 'Actual vs Predicted Readmission Status'
                        },
                        scales: {
                            x: {
                                display: true,
                                title: {
                                    display: true,
                                    text: 'Patient Number'
                                }
                            },
                            y: {
                                display: true,
                                title: {
                                    display: true,
                                    text: 'Readmission Status'
                                }
                            }
                        }
                    }
                });
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error(textStatus, errorThrown);
                alert('Prediction failed. Please try again.');
            }
        });
    });

    $('#trainBtn').click(function() {
        if (!fileContent) {
            alert('Please upload a CSV file first.');
            return;
        }

        $.ajax({
            url: '/train',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({csv: btoa(fileContent)}),
            success: function(response) {
                const trainingResult = response["Hospital Readmission Training"];
                const resultHtml = `
                    <p><strong>Best Model:</strong> ${trainingResult["Best Model"]}</p>
                    <p><strong>Train Accuracy:</strong> ${trainingResult["Train Accuracy"].toFixed(4)}</p>
                    <p><strong>Test Accuracy:</strong> ${trainingResult["Test Accuracy"].toFixed(4)}</p>
                `;
                $('#trainingResultBox').html(resultHtml);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error(textStatus, errorThrown);
                alert('Training failed. Please try again.');
            }
        });
    });
});