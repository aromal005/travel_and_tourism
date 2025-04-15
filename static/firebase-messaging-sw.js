importScripts("https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging-compat.js");

// Initialize Firebase
const firebaseConfig = {
    apiKey: "AIzaSyDtt2bdy_57SObQV9RBb50lpMqV8zBusAI",
    authDomain: "travel-tourism-d6c1f.firebaseapp.com",
    projectId: "travel-tourism-d6c1f",
    storageBucket: "travel-tourism-d6c1f.appspot.com",
    messagingSenderId: "890365706860",
    appId: "1:890365706860:web:3204d6075ff0377e2f8e49",
    measurementId: "G-ZWJ6LQP4DM"
};
firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
    console.log("Received background message:", payload);

    self.registration.showNotification(payload.notification.title, {
        body: payload.notification.body,
        icon: "/static/images/notification-icon.png" // Change this to an actual icon
    });
});
