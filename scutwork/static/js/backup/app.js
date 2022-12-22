const applicationServerPublicKey = 'BNBgYM0n-NAuwjJoVCWnoxgHXpa-Fw2wZEPHOzYft6bd7RgiR6DuVUDqr1HWxBDcjynDXjympT3zYzEr8XEL7Dc';
let isSubscribed = !1;
let swRegistration = null;

let deferredPrompt;
const btnAdd = document.querySelector('#btnAdd');

function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i)
    }
    return outputArray
}

function updateSubscriptionOnServer(subscription) {
    var notification_token = JSON.stringify(subscription)
    postData('/user/notification_token', notification_token).then(data => {console.log(data);});
}

function subscribeUser() {
    const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
    swRegistration.pushManager.subscribe({
        userVisibleOnly: !0,
        applicationServerKey: applicationServerKey
    }).then(function(subscription) {
        console.log('User is subscribed');
        updateSubscriptionOnServer(subscription);
        isSubscribed = !0
    }).catch(function(err) {
        console.log('Failed to subscribe the user: ', err)
    })
}

async function postData(url = '', data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    mode: 'same-origin', // no-cors, *cors, same-origin
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: 'same-origin', // include, *same-origin, omit
    headers: {
      'Content-Type': 'application/json'
    },
    redirect: 'manual', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });
  return response.json(); // parses JSON response into native JavaScript objects
}


function notificationCheck(result) {
    if (result === 'denied') {
        return
    }
    if (result === 'default') {
        return
    }
    subscribeUser();
    swRegistration.pushManager.getSubscription().then(function(subscription) {
        isSubscribed = !(subscription === null);
        if (isSubscribed) {
            console.log('User IS subscribed.')
        } else {
            console.log('User is NOT subscribed.')
        }
    })
}

function initializeUI() {
    const notify = document.querySelector('#notify-btn');
    notify.addEventListener('click', (e) => {
        Notification.requestPermission().then(result => {
            notificationCheck(result)
        })
    });
    if (Notification.permission === "granted") {
        notificationCheck('granted')
    }
}

if ('serviceWorker' in navigator && 'PushManager' in window) {
    navigator.serviceWorker.register('/sw.js').then(reg => {
        swRegistration = reg;
        initializeUI();
        reg.update()
    });
    let refreshing;
    navigator.serviceWorker.addEventListener('controllerchange', function() {
        if (refreshing) return;
        window.location.reload();
        refreshing = !0
    })
}

  const fireAddToHomeScreenImpression = event => {
    //will not work for chrome, untill fixed
    event.userChoice.then(choiceResult => {
      console.log(`User clicked ${choiceResult}`);
    });
    deferredPrompt = event;
    //This is to prevent `beforeinstallprompt` event that triggers again on `Add` or `Cancel` click
    window.removeEventListener(
      "beforeinstallprompt",
      fireAddToHomeScreenImpression
    );
  };
  window.addEventListener("beforeinstallprompt", fireAddToHomeScreenImpression);

btnAdd.addEventListener('click', (e) => {
  btnAdd.style.visibility = 'collapse';
  btnAdd.style.display = 'none';
  deferredPrompt.prompt();
  deferredPrompt.userChoice
    .then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the A2HS prompt');
      } else {
        console.log('User dismissed the A2HS prompt');
      }
      deferredPrompt = null;
    });
});

window.addEventListener('appinstalled', (evt) => {
  app.logEvent('app', 'installed');
});

if (window.matchMedia('(display-mode: standalone)').matches) {
  btnAdd.style.visibility = 'collapse';
  btnAdd.style.display = 'none';
}
