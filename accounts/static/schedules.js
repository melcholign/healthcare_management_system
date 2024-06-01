// Workdays array for dropdown
const WORKDAYS_MAP = {
    'Monday': 'mon',
    'Tuesday': 'tue',
    'Wednesday': 'wed',
    'Thursday': 'thu',
    'Friday': 'fri',
    'Saturday': 'sat',
    'Sunday': 'sun'
}

const addRowBtn = document.querySelector('#add-row-btn')
const updateBtn = document.querySelector('#update-btn')
const rows = document.querySelectorAll('tbody tr')

let newRow, updateMode;

addRowBtn.addEventListener('click', () => {
    newRow = addRow()

    rows.forEach(row => {
        if (row !== newRow) {
            row.disabled = true
            row.classList.add('disabled-row')
        }
    })

    disabledUpdateButton(false)
})

updateBtn.addEventListener('click', async () => {

    const inputs = newRow.querySelectorAll('input, select')
    const created = {}

    for (let input of inputs) {
        if (!input.reportValidity()) {
            return
        }

        created[input.name] = input.value
    }

    console.log(validateNewRow())

    if (!validateNewRow()) {
        return
    } else {
        generateResponseMessage('', '')
    }

    const res = await fetch('http://127.0.0.1:8000/accounts/schedules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(created)
    })

    if (res.ok) {
        newRow.id = await res.json()
        newRow.lastChild.appendChild(createDeleteButton())
        disableExistingRows(false)
        disabledUpdateButton(true)
        disableRowInputs(newRow)
        newRow = null
    }
})

function validateNewRow() {
    newInputs = newRow.querySelectorAll('select, input')

    if (newInputs[1].value >= newInputs[2].value) {
        generateResponseMessage('error', `Start time (${newInputs[1].value}) cannot be later than the end time (${newInputs[2].value}).`)
        return false
    }

    for (let row of rows) {
        const existingInputs = row.querySelectorAll('select, input')
        if (newInputs[0].value === existingInputs[0].value && !(newInputs[1].value > existingInputs[2].value || newInputs[2].value < existingInputs[1].value)) {
            console.log('error')

            generateResponseMessage('error', `Your new schedule on ${newInputs[0].value} at ${newInputs[1].value} - ${newInputs[2].value} 
            conflicts with an existing schedule at ${existingInputs[1].value} - ${existingInputs[2].value}`)
            return false
        }
    }

    return true
}


function generateResponseMessage(type, message) {
    response = document.querySelector('.response')
    response.textContent = message

    switch (type) {
        case 'error': response.style.borderBottomColor = 'red'
            break

        case 'success': response.style.borderBottomColor = 'green'
            break

        case 'pending': response.style.borderBottomColor = 'blue'
            break

        default:
            response.style.borderBottomColor = 'transparent'
    }
}

function disableRowInputs(row) {
    row.querySelectorAll('input, select').forEach(input => {
        input.disabled = true
    })
}

function disabledUpdateButton(disabled) {
    disabled ? updateBtn.classList.add('disabled') : updateBtn.classList.remove('disabled')
    updateBtn.disabled = disabled
}

function disableExistingRows(disabled) {
    rows.forEach(row => {
        if (row !== newRow) {
            row.disabled = disabled

            disabled ? row.classList.add('disabled-row') : row.classList.remove('disabled-row')
        }
    })
}

// Function to add a new row
function addRow() {
    const tr = document.createElement('tr')

    const tdWorkDay = document.createElement('td')
    const selectWorkDay = document.createElement('select')
    selectWorkDay.name = 'work_day'
    selectWorkDay.className = 'form-control workday-dropdown'
    selectWorkDay.required = true
    const placeholderOption = document.createElement('option')
    placeholderOption.value = ''
    placeholderOption.textContent = 'Select Work Day'
    placeholderOption.disabled = true
    placeholderOption.selected = true
    selectWorkDay.appendChild(placeholderOption)
    for (let workDay in WORKDAYS_MAP) {
        const option = document.createElement('option')
        option.value = WORKDAYS_MAP[workDay]
        option.textContent = workDay
        selectWorkDay.appendChild(option)
    }
    tdWorkDay.appendChild(selectWorkDay)
    tr.appendChild(tdWorkDay)

    const tdStartTime = document.createElement('td')
    const inputStartTime = document.createElement('input')
    inputStartTime.name = 'start_time'
    inputStartTime.required = true
    inputStartTime.type = 'time'
    inputStartTime.className = 'form-control start-time'
    tdStartTime.appendChild(inputStartTime)
    tr.appendChild(tdStartTime)

    const tdEndTime = document.createElement('td')
    const inputEndTime = document.createElement('input')
    inputEndTime.name = 'end_time'
    inputEndTime.required = true
    inputEndTime.type = 'time'
    inputEndTime.className = 'form-control start-time'
    tdEndTime.appendChild(inputEndTime)
    tr.appendChild(tdEndTime)

    const tdDelete = document.createElement('td')
    tr.appendChild(tdDelete)

    document.querySelector('tbody').appendChild(tr)

    return tr
}

function createDeleteButton() {
    const btnDelete = document.createElement('button')
    btnDelete.type = 'button'
    btnDelete.className = 'btn btn-danger btn-sm delete-btn'
    btnDelete.textContent = 'Delete'
    btnDelete.onclick = (e) => deleteRow(e.target)

    return btnDelete
}

function deleteRow(button) {
    const row = button.closest('tr')

    fetch('http://127.0.0.1:8000/accounts/schedules', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: row.id })
    }).then(res => {
        console.log(res.ok)
    })

    row.remove()
}

// Event listener for Update Schedules button
$("#updateSchedules").click(function () {
    // Collect schedule data
    const schedules = [];
    $("#scheduleTable tbody tr").each(function () {
        const workday = $(this).find('.workday-dropdown').val();
        const startTime = $(this).find('.start-time').val();
        const endTime = $(this).find('.end-time').val();
        if (workday && startTime && endTime) {
            schedules.push({ workday, startTime, endTime });
        }
    });

    // Send data to server (replace with actual server endpoint)
    $.ajax({
        url: '/update-schedules',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ schedules }),
        success: function (response) {
            alert('Schedules updated successfully!');
        },
        error: function (error) {
            alert('Failed to update schedules.');
        }
    });
});

// Initial display (existing schedules)
// The initial rows are hardcoded in the HTML for this example.

