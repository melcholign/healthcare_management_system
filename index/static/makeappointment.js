$(document).ready(function () {
    const schedules = [
        { doctor: "Dr. Smith", hospital: "City Hospital", schedule: "Mon 10am-12pm" },
        { doctor: "Dr. Jones", hospital: "County Hospital", schedule: "Tue 2pm-4pm" },
        { doctor: "Dr. Brown", hospital: "General Hospital", schedule: "Wed 1pm-3pm" },
        { doctor: "Dr. White", hospital: "Community Hospital", schedule: "Thu 9am-11am" },
        { doctor: "Dr. Green", hospital: "University Hospital", schedule: "Fri 3pm-5pm" },
        { doctor: "Dr. Black", hospital: "Private Clinic", schedule: "Sat 10am-12pm" },
        { doctor: "Dr. Gray", hospital: "Children's Hospital", schedule: "Sun 2pm-4pm" },
        { doctor: "Dr. Brown", hospital: "General Hospital", schedule: "Mon 1pm-3pm" },
        { doctor: "Dr. Johnson", hospital: "City Hospital", schedule: "Tue 10am-12pm" },
        { doctor: "Dr. Davis", hospital: "County Hospital", schedule: "Wed 2pm-4pm" },
        { doctor: "Dr. Wilson", hospital: "Community Hospital", schedule: "Thu 9am-11am" },
        { doctor: "Dr. Anderson", hospital: "University Hospital", schedule: "Fri 3pm-5pm" },
        { doctor: "Dr. Martinez", hospital: "Private Clinic", schedule: "Sat 10am-12pm" },
        { doctor: "Dr. Taylor", hospital: "Children's Hospital", schedule: "Sun 2pm-4pm" },
        { doctor: "Dr. Thomas", hospital: "General Hospital", schedule: "Mon 1pm-3pm" },
        { doctor: "Dr. Hernandez", hospital: "City Hospital", schedule: "Tue 10am-12pm" },
        { doctor: "Dr. Moore", hospital: "County Hospital", schedule: "Wed 2pm-4pm" },
        { doctor: "Dr. Clark", hospital: "Community Hospital", schedule: "Thu 9am-11am" }
    ];

    let currentPage = 1;
    const rowsPerPage = 10;
    let currentSchedules = schedules;
    let sortDirection = true; // true for ascending, false for descending
    let currentSortColumn = -1;

    function displayTable(page) {
        $("#scheduleTable").empty();
        const startIndex = (page - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;
        const pageSchedules = currentSchedules.slice(startIndex, endIndex);

        pageSchedules.forEach(schedule => {
            $("#scheduleTable").append(`
                <tr>
                    <td>${schedule.doctor}</td>
                    <td>${schedule.hospital}</td>
                    <td>${schedule.schedule}</td>
                    <td><button class="btn btn-primary select-btn">Select</button></td>
                </tr>
            `);
        });
    }

    function updatePagination() {
        $("#prevPage").prop("disabled", currentPage === 1);
        $("#nextPage").prop("disabled", currentPage * rowsPerPage >= currentSchedules.length);
    }

    $("#prevPage").click(function () {
        if (currentPage > 1) {
            currentPage--;
            displayTable(currentPage);
            updatePagination();
        }
    });

    $("#nextPage").click(function () {
        if (currentPage * rowsPerPage < currentSchedules.length) {
            currentPage++;
            displayTable(currentPage);
            updatePagination();
        }
    });

    $("#searchInput").on("input", function () {
        const searchText = $(this).val().toLowerCase();
        currentSchedules = schedules.filter(schedule => 
            schedule.doctor.toLowerCase().includes(searchText) ||
            schedule.hospital.toLowerCase().includes(searchText) ||
            schedule.schedule.toLowerCase().includes(searchText)
        );
        currentPage = 1;
        displayTable(currentPage);
        updatePagination();
    });

    function sortTable(columnIndex) {
        const columnKey = ["doctor", "hospital", "schedule"][columnIndex];
        currentSchedules.sort((a, b) => {
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

    // Event listener for select buttons
    $(document).on('click', '.select-btn', function () {
        alert("Schedule selected!");
    });

    // Expose the sortTable function to global scope
    window.sortTable = sortTable;
});