document.addEventListener("DOMContentLoaded", function() {
    const fightBtn = document.getElementById("fightBtn");
    const magicBtn = document.getElementById("magicBtn");
    const friendBtn = document.getElementById("friendBtn");
    const itemBtn = document.getElementById("itemBtn");
    const enemyHpBar = document.getElementById("enemyHpBar");
    const heroHpText = document.getElementById("heroHpText");
    const battleLog = document.getElementById("battleLog");

    if (enemyHpBar && enemyHpBar.getAttribute('data-hp')) {
        enemyHpBar.style.width = enemyHpBar.getAttribute('data-hp') + '%';
    }

    const storyDataEl = document.getElementById('storyData');
    const display = document.getElementById('story-text-display');
    let texts = [];
    let currentIndex = 0;

    function showNextLine() {
        if (currentIndex < texts.length) {
            display.innerHTML = texts[currentIndex];
            currentIndex++;
            const scrollContainer = document.getElementById('story-scroll-container');
            if (scrollContainer) scrollContainer.scrollTop = 0;
        } else {
            const nextNodeForm = document.getElementById('nextNodeForm');
            if(nextNodeForm) nextNodeForm.submit();
        }
    }

    if (storyDataEl && display) {
        texts = JSON.parse(storyDataEl.textContent);
        showNextLine(); 
    }

    document.addEventListener('keydown', function(event) {
        
        if (storyDataEl && display) {
            if (event.key === 'Enter') {
                event.preventDefault();
                showNextLine();
                return;
            }
        }

        const nextNodeForm = document.getElementById('nextNodeForm');
        if (!storyDataEl && display && nextNodeForm && event.key === 'Enter') {
            event.preventDefault();
            nextNodeForm.submit();
            return;
        }

        const decisionActionInput = document.getElementById('decisionAction');
        const decisionForm = document.getElementById('decisionForm');
        if (decisionActionInput && decisionForm) {
            if (event.key === '1') {
                event.preventDefault();
                decisionActionInput.value = 'ending_dragon';
                decisionForm.submit();
                return;
            } else if (event.key === '2') {
                event.preventDefault();
                decisionActionInput.value = 'ending_hero';
                decisionForm.submit();
                return;
            }
        }

        const interactiveDataEl = document.getElementById('choicesData');
        const interactiveActionInput = document.getElementById('interactiveAction');
        const interactiveForm = document.getElementById('interactiveForm');
        
        if (interactiveDataEl && interactiveActionInput && interactiveForm) {
            const rawChoices = JSON.parse(interactiveDataEl.textContent);
            const choices = rawChoices.map((choice, index) => ({
                key: (index + 1).toString(),
                action: choice.action
            }));

            const selectedChoice = choices.find(c => c.key === event.key);
            if (selectedChoice) {
                event.preventDefault();
                interactiveActionInput.value = selectedChoice.action;
                interactiveForm.submit();
                return;
            }
        }
    });

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
                    newLog.innerHTML = `<span class="log-warning" style="color:#8B0000; font-weight:bold;"> Note: ${data.error}</span>`;
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

            if (data.used_item_id) {
                const itemRow = document.getElementById("inv-row-" + data.used_item_id);
                const itemText = document.getElementById("inv-text-" + data.used_item_id);
                
                if (data.remaining_qty > 0) {
                    if (itemText) {
                        itemText.innerText = data.used_item_name + " (x" + data.remaining_qty + ")";
                    }
                } else {
                    if (itemRow) {
                        itemRow.style.display = "none"; 
                    }
                }
            }

            if (data.game_status === "won") {
                if (fightBtn) {
                    fightBtn.innerText = "Continue ➔";
                    fightBtn.setAttribute("data-status", "continue");
                    fightBtn.style.backgroundColor = "#28a745"; 
                    fightBtn.style.borderColor = "#1e7e34";
                    fightBtn.style.color = "#ffffff";
                    fightBtn.disabled = false; 
                }
            } else if (data.game_status === "lost") {
                if (fightBtn) {
                    fightBtn.innerText = "Restart";
                    fightBtn.setAttribute("data-status", "restart");
                    fightBtn.style.backgroundColor = "#8b0000"; 
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

    if (fightBtn) fightBtn.addEventListener("click", () => performAction("fight"));
    if (magicBtn) magicBtn.addEventListener("click", () => performAction("magic"));
    if (friendBtn) friendBtn.addEventListener("click", () => performAction("friend"));

    const itemMenu = document.getElementById("itemMenuContainer");
    if (itemBtn) {
        itemBtn.addEventListener("click", function() {
            if (itemMenu) {
                itemMenu.style.display = (itemMenu.style.display === "none" || itemMenu.style.display === "") ? "block" : "none";
            }
        });
    }

    document.querySelectorAll(".itemBtn").forEach(function(btn) {
        btn.addEventListener("click", function() {
            const itemId = this.getAttribute("data-item-id");
            performAction("item", itemId);
            if (itemMenu) itemMenu.style.display = "none";
        });
    });
});