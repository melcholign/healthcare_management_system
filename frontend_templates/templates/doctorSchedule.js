$(document).ready(function () {
    // Workdays array for dropdown
    const workdays = ['Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'];

    // Function to add a new row
    function addRow() {
        const newRow = `
            <tr>
                <td>
                    <select class="form-control workday-dropdown">
                        ${workdays.map(day => `<option value="${day}">${day}</option>`).join('')}
                    </select>
                </td>
                <td><input type="time" class="form-control start-time"></td>
                <td><input type="time" class="form-control end-time"></td>
                <td><button class="btn btn-danger btn-sm delete-btn">Delete</button></td>
            </tr>
        `;
        $("#scheduleTable tbody").append(newRow);
    }

    // Event listener for Add button
    $("#addRow").click(function () {
        addRow();
    });

    // Event listener for Delete buttons
    $(document).on('click', '.delete-btn', function () {
        $(this).closest('tr').remove();
    });

    // Initial row
    addRow();
});
