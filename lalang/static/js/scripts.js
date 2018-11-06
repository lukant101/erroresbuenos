var default_title="Let's Practice";
var eavesdropped_audio = [];
// flag to keep track if load_question request is for a question in a new language
var wrong_answers_log = {};
var enter_pressed = false;

function title_cap(word) {
    return word.charAt(0).toUpperCase() + word.substr(1)
}

function setTitlePractise() {
          var lang=document.getElementById("lang_select").value;
          document.getElementById("title_practice").innerHTML=default_title + " " + title_cap(lang) + "!";
}

function updateTitlePractise() {
    var lang=document.getElementById("lang_select").value;
    document.getElementById("title_practice").innerHTML=default_title + " " + title_cap(lang) + "!";
}

// plays audio when user clicks the audio button
// also keep track of played audio for marking the question
function playAudioOut() {
    var audio_out=document.getElementById('card_audio');
    audio_out.play();
    if (!(eavesdropped_audio.includes(current_language))) {
        eavesdropped_audio.push(current_language);
        console.log("Full audio log: ");
        console.log(eavesdropped_audio);
    }
    console.log("audio played for: ");
    console.log(current_language);
}

// when user plays audio, disable answer input field and change colour of send button
$(document).ready(function() {
    $("#play_button").click( function() {
        $("#user_answer").prop("disabled",true);
        if ($("#send_answer_btn").hasClass("btn-info")) {
            $("#send_answer_btn").removeClass("btn-info");
            $("#send_answer_btn").addClass("btn-warning");
        }

    });
});

// event listener: press Enter key when in Answer input field
// action: submit answer
$(document).ready(function () {
    $(document).keydown(function (event) {
        if (event.which == 13) {
            // prevent reloading of page
            event.preventDefault();
            // check whether student submitted the original answer or
            // an incorrect answer (i.e. the red submission button is visible)
            if ($("#wrong_answer_btn").css("display") === "none") {
                // use a flag to prevent double-pressing Enter key
                if (enter_pressed===false) {
                    enter_pressed=true;
                    console.log("pressed enter key");
                    sub_fld = $("#user_answer");
                    sub_fld.prop("disabled", true);
                    markAnswer();
                    console.log("marked the answer");
                    showAndSubmitAnswer();
                    console.log("submitted the answer");
                    setTimeout(function(){
                        sub_fld.prop("disabled", false);
                        enter_pressed=false;
                    },
                    500);
                }

            } else {
                // do the same as when the red "wrong" button is expressed
                hideAnswer();
                // first we cancel the timer, then we submit the wrong answer
                info = wrong_answers_log[current_language];
                clearTimeout(info.timer_id);
                submitWrongAnswer(info.stud_id, info.q_id, info.ans_corr,
                    info.audio_ans_corr, current_language);
            }
        }
    });
});

// ask for a new question when user changes language in dropdown menu
$(document).ready(function() {
    $("#lang_select").change( function() {
        current_language = $(this).val();
        console.log("Current language reset to: ");
        console.log(current_language);
        // enable or disable answer input depending if audio was heard for
        // the current question for this language
        if (eavesdropped_audio.includes(current_language)) {
            $("#user_answer").prop("disabled",true);
            if ($("#send_answer_btn").hasClass("btn-info")) {
                $("#send_answer_btn").removeClass("btn-info");
                $("#send_answer_btn").addClass("btn-warning");
                console.log("Full audio log when locking: ");
                console.log(eavesdropped_audio);
                console.log("lock and yellow button");
            }
        } else {
            $("#user_answer").prop("disabled",false);
            if ($("#send_answer_btn").hasClass("btn-warning")) {
                $("#send_answer_btn").removeClass("btn-warning");
                $("#send_answer_btn").addClass("btn-info");
                console.log("Full audio log when unlocking: ");
                console.log(eavesdropped_audio);
                console.log("unlock and back to blue button");
            }
        }
        // if  question for this language answered wrong but not yet submitted,
        // show the answer (if already not showing)
        if (current_language in wrong_answers_log &&
            $("#show_answer").css("display") === "none") {
            console.log(wrong_answers_log);
            showAnswer();
        }
        // if question for this language has not yet been answered nor submitted,
        // hide the answer (if already not hidden)
        if (!(current_language in wrong_answers_log)) {
            if ($("#show_answer").css("display") === "block") {
                hideAnswer();
            }
        }

        $.get("/next-question",
                {
                    //language : $("#lang_select").val()
                    language : current_language
                },
                load_question, "json"
        );
    });
});

// event listener: clicked the answer submit button
// sends user's answer and asks for a new question when user clicks the submit button
$(document).ready(function() {
    $("#send_answer_btn").click( function() {
        event.preventDefault();
        sub_btn = $(this);
        sub_btn.prop("disabled", true);
        markAnswer();
        showAndSubmitAnswer();
        setTimeout(function(){sub_btn.prop("disabled", false);}, 500);
    });
});

function markAnswer() {
    var user_answer = $("#user_answer").val().toLowerCase().trim();
    var answer = $("#answer").val().toLowerCase();
    var language = current_language;
    var part_of_speech = $("#part_of_speech_elem").text();
    console.log("User answer:");
    console.log(user_answer);
    console.log("Correct answer:");
    console.log(answer);
    console.log(part_of_speech);

    // answer is false be default, unless it passes in one of the tests
    var answer_correct="false";

    if (answer===user_answer) {
        answer_correct="true";
    }

    // try matching by ignoring "to" in english verbs
    if (answer_correct!="true" && language === "english" && part_of_speech === "verb") {
        console.log("english verbs clause")
        console.log(answer.slice(3));
        if (answer.slice(3)===user_answer) {
            answer_correct="true";
        }
    }

    // ignore articles in front of nouns
    if (answer_correct!="true" && part_of_speech === "noun" &&
        (language === "english" || language === "spanish")) {
        var start = user_answer.indexOf(" ");
        if (start != -1) {
            var user_answer_mod = user_answer.slice(start+1);
            if (answer===user_answer_mod) {
                answer_correct="true";
            }
        }
    }

    // if correct answer has parentheses, ignore the brackets portion and compare
    if (answer_correct!="true" && answer.indexOf("\(") != -1) {
        console.log("word with parentheses");
        var end_user_answer = user_answer.indexOf("\(");
        if (end_user_answer === -1) {
            // user did not use parentheses, so leave answer unmodified
            user_answer_mod = user_answer;
        } else {
            var user_answer_mod = user_answer.slice(0, end_user_answer);
        }
        console.log("User answer trimmed:");
        console.log(user_answer_mod);
        var end_answer = answer.indexOf("\(");
        var answer_mod = answer.slice(0, end_answer);
        console.log("Correct answer trimmed:");
        console.log(answer_mod);
        if (answer_mod===user_answer_mod) {
            answer_correct="true";
        }
    }

    $("#answer_correct").val(answer_correct);

    // log if answer is wrong, since it's not sent to server until
    // the user presses the red send button
    if (answer_correct==="false") {
        answer_info = {
            stud_id : $("#student_id").val(),
            q_id : $("#question_id").val(),
            u_answer : user_answer,
            ans_corr : $("#answer_correct").val(),
            audio_ans_corr : $("#audio_answer_correct").val(),
            lang : language
        };
        wrong_answers_log[language] = answer_info;
        console.log("added to wrong answer log:");
        console.log(wrong_answers_log[language].u_answer);
        console.log(language);
    }
}

// event listener: the red "wrong" button is pressed to submit the answer
$(document).ready(function() {
    $("#wrong_answer_btn").click(function() {
        hideAnswer();
        // first we cancel the timer, then we submit the wrong answer
        info = wrong_answers_log[current_language];
        clearTimeout(info.timer_id);

        console.log("RED BUTTON - deleting from wrong answer log: ");
        console.log(info.u_answer);
        console.log(current_language);

        submitWrongAnswer(info.stud_id, info.q_id, info.ans_corr,
            info.audio_ans_corr, current_language);
    });
});

function showAndSubmitAnswer() {
    // capture the variable values now because there is a delay when
    // submitting a wrong answer, and these values might change otherwise
    var stud_id = $("#student_id").val();
    var q_id = $("#question_id").val();
    var ans_corr = $("#answer_correct").val();
    var audio_ans_corr = $("#audio_answer_correct").val();
    var lang = current_language;
    if ($("#answer_correct").val()==="true") {
        console.log("right answer");
        var u_answer = $("#user_answer").val().trim().toLowerCase();
        $("#good_job_msg").fadeIn().delay(800).fadeOut(submitAnswer(stud_id, q_id, ans_corr, audio_ans_corr, lang, u_answer));
    } else {
        showAnswer();

        // set 30s timer for wrong answer submission
        timer_id = setTimeout(submitWrongAnswer, 20000, stud_id, q_id, ans_corr, audio_ans_corr, lang)

        // add timer id to wrong_answers_log
        wrong_answers_log[lang].timer_id = timer_id;
        console.log("added timer id: ");
        console.log(wrong_answers_log[lang].timer_id);

    }
}



function submitAnswer(stud_id, q_id, ans_corr, audio_ans_corr, lang, u_answer) {
    // flag to keep track of if load_question request is for a question in a new language
    $.post("/next-question",
            {
                // user_answer : $("#user_answer").val().trim().toLowerCase(),
                user_answer : u_answer,
                question_id : q_id,
                student_id : stud_id,
                answer_correct : ans_corr,
                audio_answer_correct : audio_ans_corr,
                language : lang
            },
            load_question, "json"
    );
}

function submitWrongAnswer(stud_id, q_id, ans_corr, audio_ans_corr, lang) {
    var wrong_answer_rec = wrong_answers_log[lang];
    var user_answer = wrong_answer_rec.u_answer;
    console.log("deleting from wrong answer log: ");
    console.log(user_answer);
    console.log(lang);
    delete wrong_answers_log[lang];

    // when submission is delayed, the active language might not be the same
    // as the language of this submission, so check
    if (current_language===lang) {
        hideAnswer();
    }


    submitAnswer(stud_id, q_id, ans_corr, audio_ans_corr, lang, user_answer);
}

function showAnswer() {
    console.log("wrong answer");
    $("#send_answer_btn").hide();
    $("#wrong_answer_btn").fadeIn();
    $("#show_answer").fadeIn();
    $("#gtranslate").fadeIn();

}

function hideAnswer() {
    console.log("hiding the answer");
    $("#show_answer").hide();
    $("#gtranslate").hide();
    $("#wrong_answer_btn").fadeOut(function(){
        $("#send_answer_btn").fadeIn();});

}

// callbback function - loads a new question
function load_question(new_question)  {
    console.log(new_question);
    var quest_obj=new_question;
    repeat_question =  (quest_obj.id === $("#question_id").val());

    // refresh the page with new question, unless it's the same question as current
    if (! repeat_question ||
        quest_obj.request_type==="GET") {
        $("#fcard").attr("src", "../static/pics/" + quest_obj.image_files.split(",")[0]);
        $("#audio_src").attr("src", "../static/audio/" + quest_obj.language.toLowerCase() + "/" + quest_obj.audio_files);
        // reload the audio source in the audio element; jQuery doesn't implement $().load(), so use JavaScript
        document.getElementById('card_audio').load();
        $("#part_of_speech_elem").text(quest_obj.part_of_speech);
        $("#word_elem").text(quest_obj.word);
        $("#user_answer").val("");
        $("#answer").val(quest_obj.word);
        $("#question_id").attr("value", quest_obj.id);
    }

    // if this question was preceded by a question (in the same language)
    // where the student listend to audio, reset to default
    if (quest_obj.request_type==="POST") {
        // remove the language of the previous question
        // from the eavesdropped_audio array (if it's there)
        // because this question has been answered
        language_index = eavesdropped_audio.indexOf(quest_obj.prev_q_lang);
        if (language_index != -1) {
            eavesdropped_audio.splice(language_index,1);

            // update view only if it's not the same question
            if (! repeat_question) {

                // enable the answer input for this language
                $("#user_answer").prop("disabled",false);

                // change send button colour back to default
                $("#send_answer_btn").removeClass("btn-warning");
                $("#send_answer_btn").addClass("btn-info");
                console.log("Full audio log when unlocknig in LOAD QUESTION: ");
                console.log(eavesdropped_audio);
                console.log("unlock and back to blue button - FROM LOAD QUESTION");
            }
        }
        // it's a new question, so hide the answer, if already not hidden
        if ($("#show_answer").css("display") === "block") {
            hideAnswer();
        }
    }
}
