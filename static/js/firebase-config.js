// // Import the functions you need from the SDKs you need
// import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
// import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-analytics.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBvdnaG71l2jAC_Mu55FNQjTZEMiCCI_j4",
  authDomain: "finance-tracker-73ae7.firebaseapp.com",
  projectId: "finance-tracker-73ae7",
  storageBucket: "finance-tracker-73ae7.firebasestorage.app",
  messagingSenderId: "582815627290",
  appId: "1:582815627290:web:7a73620ded70111693b9a3",
  measurementId: "G-KQ1D4N1X38",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
