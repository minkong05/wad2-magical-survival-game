document.addEventListener("DOMContentLoaded", function() {

    const fightBtn = document.getElementById("fightBtn");
    const magicBtn = document.getElementById("magicBtn");
    const friendBtn = document.getElementById("friendBtn");
    const itemBtn = document.getElementById("itemBtn");
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


    function setButtonsDisabled(disabled) {
        if (fightBtn) fightBtn.disabled = disabled;
        if (magicBtn) magicBtn.disabled = disabled;
        if (friendBtn) friendBtn.disabled = disabled;
        if (itemBtn) itemBtn.disabled = disabled;
        document.querySelectorAll(".itemBtn").forEach(btn => btn.disabled = disabled);
    }

    function performAction(actionType, itemId = null) {
        if (fightBtn && fightBtn.getAttribute("data-status") === "continue") {
            const form = document.getElementById("nextNodeForm");
            if (form) {
                form.submit();
            } else {
                window.location.reload(); 
            }
            return;
        }

        if (fightBtn && fightBtn.getAttribute("data-status") === "restart") {
            window.location.href = "/game/restart/"; 
            return;
        }

        setButtonsDisabled(true);

        const body = { "action_type": actionType };
        if (itemId !== null && itemId !== undefined) body["item_id"] = itemId;

        fetch("/game/api/attack/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                if (battleLog) {
                    const newLog = document.createElement("p");
                    newLog.innerHTML = `<span class="log-warning"> Note: ${data.error}</span>`;
                    newLog.style.borderBottom = "1px solid rgba(122, 92, 35, 0.2)";
                    newLog.style.paddingBottom = "8px";
                    battleLog.appendChild(newLog);
                    battleLog.scrollTop = battleLog.scrollHeight;
                }
                setButtonsDisabled(false);
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
                if (fightBtn) {
                    fightBtn.innerText = "Continue ➔";
                    fightBtn.setAttribute("data-status", "continue");
                    fightBtn.classList.replace("btn-danger", "btn-success"); 
                    fightBtn.disabled = false; 
                }
            } else if (data.game_status === "lost") {
                if (fightBtn) {
                    fightBtn.innerText = "Restart";
                    fightBtn.setAttribute("data-status", "restart");
                    fightBtn.classList.replace("btn-danger", "btn-dark"); 
                    fightBtn.disabled = false; 
                }
            } else {
                setButtonsDisabled(false);
            }
        })
        .catch(error => {
            console.error("Battle Error:", error);
            setButtonsDisabled(false);
        });
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

    if (friendBtn) {
        friendBtn.addEventListener("click", function() {
            performAction("friend");
        });
    }

    if (itemBtn) {
        itemBtn.addEventListener("click", function() {
            performAction("item");
        });
    }

    document.querySelectorAll(".itemBtn").forEach(function(btn) {
        btn.addEventListener("click", function() {
            const itemId = this.getAttribute("data-item-id");
            performAction("item", itemId);
        });
    });
});
