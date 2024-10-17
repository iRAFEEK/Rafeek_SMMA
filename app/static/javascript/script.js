    function updateNotificationCount() {
        fetch('{{ url_for("main.get_unread_notification_count") }}')
            .then(response => response.json())
            .then(data => {
                document.querySelector('.badge-danger').innerText = data.count;
            });
    }

    // Update every 30 seconds (adjust as needed)
    setInterval(updateNotificationCount, 30000);
