$(function () {

    var winner = ' ';
    var grid = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];

    function showPage(page) {
        // $('.page').hide()
        // $('#' + page).show()
        window.location.replace(page)
    }

    $('form.follow').submit(function(event) {
        event.preventDefault();

        var data = $(this).serializeArray().reduce((dict, field) => {
            dict[field.name] = field.value;
            return dict;
        }, {});

        data['follow'] = true;

        console.log(data)
        
        fetch("/follow", {
            method: "POST",
            mode: "cors",
            cache: "no-cache",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json"
            },
            redirect: "follow",
            referrer: "no-referrer",
            body: JSON.stringify(data)
        })
        .then(response => {
            return response.json();
        })
        .then(response => {
            console.log(response);

            if(response.status == "OK")
                showPage('home')
                // renderView();
                // resetGame();
        })
    })

    $('button.signup').click(() => {
        showPage("signup");
    })

    $('button.login').click(() => {
        showPage("login");
    })

    $('button.reset').click(() => {
        resetGame();
    })

    $('button.post-new').click(() => {
        addItem('new');
    })

    $('button.post-reply').click(() => {
        addItem('reply');
    })

    $('button.post-retweet').click(() => {
        data = {
            // "content": 
            "childType": "tweet",
        }
        fetch("/additem", {
            method: "POST",
            mode: "cors",
            cache: "no-cache",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": data['csrfmiddlewaretoken']
            },
            redirect: "follow",
            referrer: "no-referrer",
            body: JSON.stringify(data)
        })
        .then(response => {
            return response.json();
        })
        .then(response => {
            console.log(response);
            
            // if(response.status == "OK")
                
        })
    })

    $('button.like').click(function() {
        var id = this.id.split("-")[1];
        var data = {
            "id": id,
        }
        console.log(data)
        fetch("/like", {
            method: "POST",
            mode: "cors",
            cache: "no-cache",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json"
            },
            redirect: "follow",
            referrer: "no-referrer",
            body: JSON.stringify(data)
        })
        .then(response => {
            return response.json();
        })
        .then(response => {
            console.log(response);
            
            if(response.status == "OK") {
                $('span.likes-' + id).html(response.likes)
            }
        })
        
    })

    $('#signupForm').submit(function(event) {
        event.preventDefault();

        var data = $(this).serializeArray().reduce((dict, field) => {
            dict[field.name] = field.value;
            return dict;
        }, {});
        
        fetch("/adduser", {
            method: "POST",
            mode: "cors",
            cache: "no-cache",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json"
            },
            redirect: "follow",
            referrer: "no-referrer",
            body: JSON.stringify(data)
        })
        .then(response => {
            return response.json();
        })
        .then(response => {
            console.log(response);
            
            if(response.status == "OK")
                // renderView();
                // $("input.verify-email").val(data["email"]) // also save as cookie?
                showPage("verify?email="+data["email"]);
        })
    })

    $('#verifyForm').submit(function(event) {
        event.preventDefault();

        var data = $(this).serializeArray().reduce((dict, field) => {
            dict[field.name] = field.value;
            return dict;
        }, {});
        
        fetch("/verify", {
            method: "POST",
            mode: "cors",
            cache: "no-cache",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json"
            },
            redirect: "follow",
            referrer: "no-referrer",
            body: JSON.stringify(data)
        })
        .then(response => {
            return response.json();
        })
        .then(response => {
            console.log(response);
            
            if(response.status == "OK")
                // renderView();
                showPage("login");
        })
    })

    $('#loginForm').submit(function(event) {
        event.preventDefault();

        var data = $(this).serializeArray().reduce((dict, field) => {
            dict[field.name] = field.value;
            return dict;
        }, {});
        
        fetch("/login", {
            method: "POST",
            mode: "cors",
            cache: "no-cache",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json"
            },
            redirect: "follow",
            referrer: "no-referrer",
            body: JSON.stringify(data)
        })
        .then(response => {
            return response.json();
        })
        .then(response => {
            console.log(response);

            if(response.status == "OK")
                showPage('home')
                // renderView();
                // resetGame();
        })
    })

    $('button.logout').click(function(event) {
        fetch("/logout", {
            method: "GET",
            mode: "cors",
            cache: "no-cache",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json"
            },
            redirect: "follow",
            referrer: "no-referrer",
        })
        .then(response => {
            return response.json();
        })
        .then(response => {
            console.log(response);

            if(response.status == "OK")
                // renderView();
                showPage("login");
        })
    })

    // $('form.search').submit(function(event) {
    //     event.preventDefault();

    //     var data = $(this).serializeArray().reduce((dict, field) => {
    //         dict[field.name] = field.value;
    //         return dict;
    //     }, {});
        
    //     fetch("/search", {
    //         method: "POST",
    //         mode: "cors",
    //         cache: "no-cache",
    //         credentials: "same-origin",
    //         headers: {
    //             "Content-Type": "application/json"
    //         },
    //         redirect: "follow",
    //         referrer: "no-referrer",
    //         body: JSON.stringify(data)
    //     })
    //     .then(response => {
    //         return response.json();
    //     })
    //     .then(response => {
    //         console.log(response);

    //         if(response.status == "OK")
    //             showPage('home')
    //     });
    // });

    function addItem(type) {
        $('form.post-' + type).submit(function(event) {
            event.preventDefault();
    
            var data = $(this).serializeArray().reduce((dict, field) => {
                dict[field.name] = field.value;
                return dict;
            }, {});
            data['childType'] = type=='new' ? null : type;
            
            fetch("/additem", {
                method: "POST",
                mode: "cors",
                cache: "no-cache",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": data['csrfmiddlewaretoken']
                },
                redirect: "follow",
                referrer: "no-referrer",
                body: JSON.stringify(data)
            })
            .then(response => {
                return response.json();
            })
            .then(response => {
                console.log(response);
                
                // if(response.status == "OK")
                    
            })
        })
    }

    function getCookie(cname) {
        var name = cname + "=";
        var ca = document.cookie.split(';');
        for(var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) == 0) {
                return c.substring(name.length, c.length);
            }
        }
        return "";
    }

});