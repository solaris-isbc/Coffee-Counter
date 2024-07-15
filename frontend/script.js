window.onload = () => {

    let totalAmount = 0;
    const apiEndpoint = 'http://127.0.0.1:8000/daily_entries/'

    const getCurrentDate = () => {
        const pad = function(num) { return ('00'+num).slice(-2) };

        const date = new Date();
        return `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())}`;
    };

    const updateUI = (totalAmount) => {
        document.getElementById('coffeeCount').textContent = totalAmount;
    };

    const persistData = (totalAmount) => {
        const request = new XMLHttpRequest(); 
        const url = `${apiEndpoint}`;
        request.open('POST', url);
        request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        request.send(
            JSON.stringify(
                {
                    'date': getCurrentDate(),
                    'amount': totalAmount 
                }
            )
        );
    };

    const fetchInitialData = () => {
        const request = new XMLHttpRequest();
        const url = `${apiEndpoint}${getCurrentDate()}`;
        request.open('GET', url);
        
        request.onload = () => {
            const data = JSON.parse(request.responseText);
            const amount = parseFloat(data.amount);
            totalAmount = amount;
            updateUI(totalAmount);
        };

        request.send();
    };

    const changeAmount = (event) => {
        const amount = parseFloat(event.currentTarget.dataset.delta);
        totalAmount = Math.max(totalAmount + amount, 0);

        updateUI(totalAmount);
        persistData(amount);
    };

    document.querySelectorAll('.change-btn').forEach((elem) => elem.addEventListener('click', changeAmount));
    fetchInitialData();
};