$(document).ready(function () {
    const appointments = [
        { date: '2024-06-01', time: '3pm-5pm', doctor: 'Dr. Anderson', status: 'pending' },
        { date: '2024-06-02', time: '10am-12pm', doctor: 'Dr. Black', status: 'missed' },
        { date: '2024-06-03', time: '1pm-3pm', doctor: 'Dr. Brown', status: 'complete' },
        // Add more appointments as needed
    ];

    let currentPage = 1;
    const rowsPerPage = 10;
    let currentAppointments = appointments;
    let sortDirection = true; // true for ascending, false for descending
    let currentSortColumn = -1;

    function displayTable(page) {
        $("#appointmentTableBody").empty();
        const startIndex = (page - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;
        const pageAppointments = currentAppointments.slice(startIndex, endIndex);

        pageAppointments.forEach(appointment => {
            const row = `
                <tr>
                    <td>${appointment.date}</td>
                    <td>${appointment.time}</td>
                    <td>${appointment.doctor}</td>
                    <td>${appointment.status}</td>
                    <td class="table-actions">
                        ${appointment.status === 'pending' ? 
                            '<button class="btn btn-danger btn-sm cancel-btn">Cancel</button>' : 
                            '<button class="btn btn-warning btn-sm reschedule-btn">Reschedule</button>'}
                    </td>
                </tr>
            `;
            $("#appointmentTableBody").append(row);
        });
    }

    function updatePagination() {
        $("#prevPage").prop("disabled", currentPage === 1);
        $("#nextPage").prop("disabled", currentPage * rowsPerPage >= currentAppointments.length);
    }

    $("#prevPage").click(function () {
        if (currentPage > 1) {
            currentPage--;
            displayTable(currentPage);
            updatePagination();
        }
    });

    $("#nextPage").click(function () {
        if (currentPage * rowsPerPage < currentAppointments.length) {
            currentPage++;
            displayTable(currentPage);
            updatePagination();
        }
    });

    $("#searchInput").on("input", function () {
        const searchText = $(this).val().toLowerCase();
        currentAppointments = appointments.filter(appointment =>
            appointment.date.toLowerCase().includes(searchText) ||
            appointment.time.toLowerCase().includes(searchText) ||
            appointment.doctor.toLowerCase().includes(searchText) ||
            appointment.status.toLowerCase().includes(searchText)
        );
        currentPage = 1;
        displayTable(currentPage);
        updatePagination();
    });

    function sortTable(columnIndex) {
        const columnKey = ["date", "time", "doctor", "status"][columnIndex];
        currentAppointments.sort((a, b) => {
            if (a[columnKey] < b[columnKey]) return sortDirection ? -1 : 1;
            if (a[columnKey] > b[columnKey]) return sortDirection ? 1 : -1;
            return 0;
        });
        sortDirection = !sortDirection;

        // Update sort indicators
        $("th .sort-indicator").removeClass("sort-asc sort-desc");
        const indicatorClass = sortDirection ? "sort-asc" : "sort-desc";
        $("th").eq(columnIndex).find(".sort-indicator").addClass(indicatorClass);

        currentPage = 1;
        displayTable(currentPage);
        updatePagination();
    }

    // Initial display
    displayTable(currentPage);
    updatePagination();

    // Event listeners for buttons
    $(document).on('click', '.cancel-btn', function () {
        alert("Appointment cancelled!");
    });

    $(document).on('click', '.reschedule-btn', function () {
        alert("Appointment rescheduled!");
    });

    // Expose the sortTable function to global scope
    window.sortTable = sortTable;
});
