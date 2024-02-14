document.addEventListener('DOMContentLoaded', function () {
    const startRecordBtn = document.getElementById('startRecord');
    const stopRecordBtn = document.getElementById('stopRecord');
    const audioElement = document.getElementById('audio');
    const timerElement = document.getElementById('timer');
    const NoterizeElementBtn = document.getElementById('Noterize');


    let mediaRecorder;
    let recordedChunks = [];
    let startTime;
    let timerInterval;

    startRecordBtn.addEventListener('click', startRecording);
    stopRecordBtn.addEventListener('click', stopRecording);
    NoterizeElementBtn.addEventListener('click', Noterizeing);

    function Noterizeing(){
        NoterizeElementBtn.innerHTML = "Processing...";
    }

    function startRecording() {
        startTime = new Date().getTime();
        timerElement.style.color = "red";
        updateTimer();

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(function (stream) {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                startRecordBtn.disabled = true;
                stopRecordBtn.disabled = false;
                recordedChunks = [];

                mediaRecorder.addEventListener('dataavailable', function (e) {
                    recordedChunks.push(e.data);
                });

                mediaRecorder.addEventListener('stop', function () {
                    const blob = new Blob(recordedChunks, { type: 'audio/wav' });
                    const audioURL = URL.createObjectURL(blob);
                    audioElement.src = audioURL;

                    clearInterval(timerInterval); // Stop updating the timer
                    timerElement.innerHTML = "";
                    timerElement.style.color = "";

                    const endTime = new Date().getTime();
                    const duration = (endTime - startTime) / 1000;
                    console.log("Recording duration: " + duration + " seconds");
                });
            })
            .catch(function (err) {
                console.error('Error accessing microphone:', err);
            });
    }

    function stopRecording() {
        mediaRecorder.stop();
        startRecordBtn.disabled = false;
        stopRecordBtn.disabled = true;
    }

    function updateTimer() {
        let elapsedSeconds = 0;
        timerInterval = setInterval(function () {
            const currentTime = new Date().getTime();
            elapsedSeconds = Math.floor((currentTime - startTime) / 1000);
            timerElement.innerHTML = `Recording: ${elapsedSeconds} seconds`;
        }, 1000);
    }
});
