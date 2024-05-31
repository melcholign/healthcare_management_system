$(document).ready(function () {
    // Workdays array for dropdown
    const workdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

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
});
