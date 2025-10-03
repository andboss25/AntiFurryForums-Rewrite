
async function authoption(enpoint,completion){
    if (document.getElementById('policy').checked != true) {
        document.getElementById("error").style.color = 'red';
        document.getElementById("error").innerHTML = 'Please agree to the privacy policy'
        return;
    }
    let username = document.getElementById("username").value
    let password = document.getElementById("password").value

    let resp = await fetch(`/api/user/${enpoint}`,{
            body: JSON.stringify({ username: username, password: password}),
            method: "POST",
            headers: {
            "Content-Type": "application/json",
        },
    })

    let parsed_resp = await resp.json()
    
    if ('error' in parsed_resp) {
        document.getElementById("error").style.color = 'red';
        document.getElementById("error").innerHTML = parsed_resp['error']
    } else if ('token' in parsed_resp) {
        document.getElementById("error").style.color = 'green';
        document.getElementById("error").innerHTML = completion
        localStorage.setItem('token',parsed_resp['token'])
    }
}

async function login(){
    authoption("login","Logged into account!")
}

async function signup(){
    authoption("signup","Created account!")
}