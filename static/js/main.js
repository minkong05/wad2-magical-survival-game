document.addEventListener("DOMContentLoaded", function() {
    

    const fightBtn = document.getElementById("fightBtn");
    const magicBtn = document.getElementById("magicBtn");
    const enemyHpBar = document.getElementById("enemyHpBar");
    const heroHpText = document.getElementById("heroHpText");
    const battleLog = document.getElementById("battleLog");

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }


    function performAction(actionType) {
        if (fightBtn) fightBtn.disabled = true;
        if (magicBtn) magicBtn.disabled = true;


        fetch("/api/attack/", { 
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "action_type": actionType  
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                enableButtons();
                return;
            }


            if (enemyHpBar) {
                enemyHpBar.style.width = data.enemy_hp_percent + "%";
            }
            
            if (heroHpText) {
                heroHpText.innerText = "HP: " + data.player_hp;
            }

            if (battleLog) {
                const newLog = document.createElement("p");
                newLog.innerHTML = data.log_message;
                newLog.style.color = "#2B1A0D"; 
                newLog.style.borderBottom = "1px solid rgba(122, 92, 35, 0.2)"; 
                newLog.style.paddingBottom = "8px";
                
                battleLog.appendChild(newLog);
                
                battleLog.scrollTop = battleLog.scrollHeight;
            }


            if (data.game_status === "won") {
                if (fightBtn) fightBtn.innerText = "Victory!";
            } else if (data.game_status === "lost") {
                if (fightBtn) fightBtn.innerText = "Game Over";
            } else {
                enableButtons();
            }
        })
        .catch(error => {
            console.error("Battle Error:", error);
            enableButtons();
        });
    }

    function enableButtons() {
        if (fightBtn) fightBtn.disabled = false;
        if (magicBtn) magicBtn.disabled = false;
    }


    if (fightBtn) {
        fightBtn.addEventListener("click", function() {
            performAction("fight"); 
        });
    }

    if (magicBtn) {
        magicBtn.addEventListener("click", function() {
            performAction("magic"); 
        });
    }
});