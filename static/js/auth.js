document.addEventListener('DOMContentLoaded', function() {
    const auth = firebase.auth();
    const googleSignInBtn = document.getElementById('googleSignIn');
    
    // Handle Google Sign In
    googleSignInBtn.addEventListener('click', function(e) {
        e.preventDefault();
        const provider = new firebase.auth.GoogleAuthProvider();
        
        auth.signInWithPopup(provider)
            .then((result) => {
                // Get the Google Access Token
                const credential = result.credential;
                const token = credential.accessToken;
                const user = result.user;

                // Send the token to your Flask backend
                return fetch('/google-auth', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        token: token,
                        uid: user.uid,
                        email: user.email,
                        displayName: user.displayName
                    })
                });
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/dashboard';
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Authentication failed. Please try again.');
            });
    });

    // Handle regular form login
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        auth.signInWithEmailAndPassword(email, password)
            .then((userCredential) => {
                return userCredential.user.getIdToken();
            })
            .then(token => {
                // Submit the form with the token
                const tokenInput = document.createElement('input');
                tokenInput.type = 'hidden';
                tokenInput.name = 'token';
                tokenInput.value = token;
                loginForm.appendChild(tokenInput);
                loginForm.submit();
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Login failed. Please check your credentials.');
            });
    });
});

