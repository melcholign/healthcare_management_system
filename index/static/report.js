document.addEventListener("DOMContentLoaded", function () {
    var coll = document.getElementsByClassName("collapsible");
    for (var i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function () {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
});

const deletedPrescriptionIDs = []

function post() {
    let isValidPost = true

    const newDiagnosisInputs = document.querySelectorAll('.diagnosis .new input')
    const newDiagnoses = []

    for (let input of newDiagnosisInputs) {
        if (!input.reportValidity()) {
            return
        }

        newDiagnoses.push(input.value)
    }

    const newPrescriptionRows = document.querySelectorAll('.prescription .new tbody tr')
    const newPrescriptions = []

    for (let row of newPrescriptionRows) {
        const inputs = row.querySelectorAll('input, select')
        const prescription = {}

        for (let input of inputs) {
            if (!input.reportValidity()) {
                return
            }

            if (input.type == 'radio') {
                if (input.checked) {
                    prescription.before_meal = true
                }
            } else {
                prescription[input.name] = input.value
            }
        }

        newPrescriptions.push(prescription)
    }

    //document.querySelector('body').setAttribute('disabled', '')

    const appointmentID = window.location.href.slice(window.location.href.lastIndexOf('/') + 1)
    fetch(`http://127.0.0.1:8000/attend_appointment/${appointmentID}`, {
        method: 'POST',
        body: JSON.stringify(
            {
                cured_diagnosis_ids: getCuredDiagnosisIDs(),
                deleted_prescription_ids: deletedPrescriptionIDs,
                new_diagnoses: newDiagnoses,
                new_prescriptions: newPrescriptions,
            }
        )
    }).then(res => {
        console.log(newPrescriptions)

        if(res.ok) {
            window.location.replace(`http://127.0.0.1:8000/accounts/account_page/doctor_appointment_list`)
        }
    })

}

function deletePrescriptionRow(button) {
    const targetRow = button.parentElement.parentElement;
    deletedPrescriptionIDs.push(parseInt(targetRow.id))
    targetRow.remove();
}

function addDiagnosisRow(button) {
    const targetSection = button.parentElement.parentElement.classList[0]
    const tbody = document.querySelector(`.${targetSection} .new tbody`)

    const tr = document.createElement('tr')
    const td = document.createElement('td')
    const input = document.createElement('input')

    input.required = true
    input.classList.add('form-control')
    input.name = 'disease'

    td.appendChild(input)
    tr.appendChild(td)
    tbody.append(tr)
}

function addPrescriptionRow(button) {
    const targetSection = button.parentElement.parentElement.classList[0]
    const tbody = document.querySelector(`.${targetSection} .new tbody`)

    const tr = document.createElement('tr')
    const tdList = []

    const tdMedicine = document.createElement('td')
    const inputMedicine = document.createElement('input')
    inputMedicine.required = true
    inputMedicine.classList.add('form-control')
    inputMedicine.name = 'medicine'
    tdMedicine.appendChild(inputMedicine)
    tdList.push(tdMedicine)

    const tdDosage = document.createElement('td')
    const inputDosage = document.createElement('input')
    inputDosage.required = true
    inputDosage.type = 'number'
    inputDosage.classList.add('form-control')
    inputDosage.name = 'dosage'
    tdDosage.appendChild(inputDosage)
    tdList.push(tdDosage)

    const tdTiming = document.createElement('td')
    const selectTiming = document.createElement('select')
    const timingValues = ['morning', 'noon', 'afternoon', 'evening', 'night', 'midnight']
    selectTiming.required = true
    selectTiming.classList.add('form-control')
    selectTiming.name = 'timing'
    const placeholderTiming = document.createElement('option')
    placeholderTiming.value = ''
    placeholderTiming.text = 'Select a timing'
    placeholderTiming.disabled = true
    placeholderTiming.selected = true
    selectTiming.appendChild(placeholderTiming)
    timingValues.forEach(value => {
        const option = document.createElement('option')
        option.value = value
        option.text = value.slice(0, 1).toUpperCase() + value.slice(1)
        selectTiming.appendChild(option)
    })
    tdTiming.appendChild(selectTiming)
    tdList.push(tdTiming)

    const tdMeal = document.createElement('td')
    const nthRow = tbody.childNodes.length + 1

    const divBefore = document.createElement('div')
    const inputBefore = document.createElement('input')
    const labelBefore = document.createElement('label')
    divBefore.className = 'form-check form-check-inline'
    inputBefore.required = true
    inputBefore.classList.add('form-check-input')
    inputBefore.id = `before-meal${nthRow}`
    inputBefore.type = 'radio'
    inputBefore.name = `before_meal${nthRow}`
    labelBefore.classList.add('form-check-label')
    labelBefore.setAttribute('for', inputBefore.id)
    labelBefore.textContent = 'Before Meal'
    divBefore.appendChild(inputBefore)
    divBefore.appendChild(labelBefore)
    tdMeal.appendChild(divBefore)

    const divAfter = document.createElement('div')
    const inputAfter = document.createElement('input')
    const labelAfter = document.createElement('label')
    divAfter.className = 'form-check form-check-inline'
    inputAfter.required = true
    inputAfter.classList.add('form-check-input')
    inputAfter.id = `after-meal${nthRow}`
    inputAfter.type = 'radio'
    inputAfter.name = `before_meal${nthRow}`
    labelAfter.classList.add('form-check-label')
    labelAfter.setAttribute('for', inputAfter.id)
    labelAfter.textContent = 'After Meal'
    divAfter.appendChild(inputAfter)
    divAfter.appendChild(labelAfter)
    tdMeal.appendChild(divAfter)

    tdList.push(tdMeal)

    tdList.forEach(td => tr.appendChild(td))

    tbody.append(tr)
}

function getCuredDiagnosisIDs() {
    const curedDiagnosisIDs = []
    const previousDiagnosisRows = document.querySelectorAll('.diagnosis .previous tbody tr')

    previousDiagnosisRows.forEach(row => {
        const isCured = row.querySelector(`input[type=checkbox]`).checked

        if (isCured) {
            curedDiagnosisIDs.push(parseInt(row.id))
        }
    })

    return curedDiagnosisIDs
}



