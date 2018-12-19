const DEFAULT_TITLE="Let's Practice";
var eavesdropped_audio = [];
// flag to keep track if load_question request is for a question in a new language
var wrong_answers_log = {};
var enter_pressed = false;
var signup_btn_timer_id = "";
var all_answers = [];
var current_ids = {};
// bucket where image and audio files are stored
const bucket = "https://storage.googleapis.com/my-project-1542060211099.appspot.com/static/";

function title_cap(word) {
    return word.charAt(0).toUpperCase() + word.substr(1)
}

function updateTitlePractise() {
    $(document).ready(function() {
        const title_elem = document.getElementById("title_practice");
        if (title_elem !== null) {
            var lang=document.getElementById("lang_select").value;
            title_elem.innerHTML=DEFAULT_TITLE + " " + title_cap(lang) + "!";
        }
    });
}

function load_answers() {
    // the answers array is wrapped in a string in a hidden form field
    // so turn it back into an array
    $(document).ready(function() {
        let answers = $("#answers").val().slice(2,-2);
        console.log("marking answer. Answers after slicing: ", answers);
        answers = answers.split("', '");
        console.log("marking answer. Answers after splitting: ", answers);
        answers.forEach(function(elem, i, a) {
            a[i]=elem.toLowerCase().trim();
        });
        all_answers = answers;
        console.log("answers saved in a variable");
        $("#answers").remove();
    });
}

// read the question and student ids from the DOM and then remove these elements
function capture_ids() {
    $(document).ready(function() {
        current_ids.student_id = $("#student_id").val();
        console.log("captured student id: ", current_ids.student_id);
        $("#student_id").remove();
        current_ids.question_id = $("#question_id").val();
        console.log("captured question id: ", current_ids.question_id);
        $("#question_id").remove();
    });
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
            $("#send_answer_btn").addClass("btn-success");
        }

    });
});

// event listener: resizing of the window
// we need to adjust the bottom margin of the images container
$( window ).resize(function() {
    set_height_img_container();
});

// event listener: Enter key pressed;
// action: submit answer
$(document).ready(function () {
    $(document).keydown(function (event) {
        let code = event.which || event.keyCode;
        if (code == 13) {
            console.log("pressed the enter key");
            // prevent reloading of page
            event.preventDefault();
            // check whether student submitted the original answer or
            // an incorrect answer (i.e. the red submission button is visible)
            if ($("#wrong_answer_btn").css("display") === "none") {
                // use a flag to prevent double-pressing Enter key
                if (enter_pressed===false) {
                    enter_pressed=true;
                    sub_fld = $("#user_answer");
                    sub_fld.prop("disabled", true);
                    $("#send_answer_btn").prop("disabled",true);
                    showAndSubmitAnswer(markAnswer());
                }

            } else {
                console.log("red button is visible, so hide the answer");
                // do the same as when the red "wrong" button is expressed
                hideAnswer();
                console.log("after hideAnswer()");
                // first we cancel the timer, then we submit the wrong answer
                info = wrong_answers_log[current_language];
                clearTimeout(info.timer_id);
                submitWrongAnswer(info);
            }
        }
    });
});


// when user clicks the sign-up prompt button, hide it and cancel the timer
$(document).ready(function() {
    $("#prod_signup").click( function() {
        clearTimeout(signup_btn_timer_id);
        $("#prod_signup").hide();
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
                $("#send_answer_btn").addClass("btn-success");
                console.log("Full audio log when locking: ");
                console.log(eavesdropped_audio);
                console.log("lock and yellow button");
            }
        } else {
            $("#user_answer").prop("disabled",false);
            if ($("#send_answer_btn").hasClass("btn-success")) {
                $("#send_answer_btn").removeClass("btn-success");
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
        console.log("just pressed the first button");
        sub_btn = $(this);
        console.log($(this));
        console.log("after $this statement");
        sub_btn.prop("disabled", true);
        $("#user_answer").prop("disabled",true);
        console.log("submit button disabled");
        console.log($(this));
        console.log($(this).css("display"));
        showAndSubmitAnswer(markAnswer());
        console.log("button display at the end of send button pressed event: ");
        console.log($("#send_answer_btn").css("display"));
    });
});

//event listener: clicked the Translate button
$(document).ready(function() {
    $("#translate-btn").click(function() {
        console.log("clicked the translate button");
        $.post("/translate", {
            input_text : $("#translate_text_input").val(),
            input_language : current_language
        }, show_translation, "json");
    });
});

function show_translation(output_text) {
    console.log("about to provide the translated answer")
    $("#translate_text_output").html(output_text);
    $("#translate_text_output").fadeIn();
}

function markAnswer() {
    var user_answer = $("#user_answer").val().toLowerCase().trim();
    user_answer = sanitize(user_answer);
    const language = current_language;
    const part_of_speech = $("#part_of_speech_elem").text();
    console.log("User answer: ", user_answer);
    console.log("Correct answer: ", all_answers);
    console.log(part_of_speech);

    var answer_correct = false;

    // check that the answer is not an empty string, then check whether
    // it's correct
    if (user_answer !=="") {
        answer_correct = arrayIncludes(user_answer, all_answers);

        // ignore articles in front of nouns and check again
        if (answer_correct!=true && part_of_speech === "noun" &&
            (language === "english" || language === "spanish")) {
            var start = user_answer.indexOf(" ");
            if (start != -1) {
                var user_answer_mod = user_answer.slice(start+1);
                answer_correct = arrayIncludes(user_answer_mod, all_answers);
            }
        }
    }


    console.log("answer correct: ", answer_correct);

    if (answer_correct && ($("#scoreCount").length)) {
        console.log("entered the increment clause")
        incrementScore();
    }

    console.log("before saving to answer_info:")
    console.log("current_ids.student_id: ", current_ids.student_id)
    console.log("current_ids.question_id: ", current_ids.question_id)

    answer_info = {
        student_id : current_ids.student_id,
        question_id : current_ids.question_id,
        user_answer : user_answer,
        answer_correct : answer_correct,
        audio_answer_correct : false,
        language : language
    };

    // log if answer is wrong, since it's not sent to server until
    // the user presses the red send button
    if (! answer_correct) {
        wrong_answers_log[language] = answer_info;
        console.log("added to wrong answer log:");
        console.log(wrong_answers_log[language].user_answer);
        console.log(language);
    }

    return answer_info
}

function sanitize(input) {
    return input
         .replace(/;/g, ".")
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "")
         .replace(/\\/g, "&#92;")
         .replace(/{/g, "&#123;")
         .replace(/}/g, "&#125;");
}

function incrementScore() {
    var scoreCount = parseInt($("#scoreCount").html());
    console.log("the score count retrieved: ", scoreCount);
    scoreCount++;
    console.log("score increased");
    console.log("the increased score as integer: ", scoreCount);
    $("#scoreCount").html(scoreCount.toString());
    console.log("the score as a string: ", scoreCount.toString());
}

function arrayIncludes(elem, array_in) {
    for (let a of array_in) {
        if (elem === a) {
            return true;
        console.log("looking in array for: ", elem);
        console.log("matching to: ", a, "and the result: ", (elem === a))
        }
    }

    return false;
}

// event listener: the red "wrong" button is pressed to submit the answer
$(document).ready(function() {
    $("#wrong_answer_btn").click(function() {
        console.log("RED BUTTON - submitting wrong answer launched");
        hideAnswer();
        // first we cancel the timer, then we submit the wrong answer
        info = wrong_answers_log[current_language];
        clearTimeout(info.timer_id);

        submitWrongAnswer(info);
    });
});

function showAndSubmitAnswer(answer_info) {
    console.log("Document has focus? ", document.hasFocus());
    if (answer_info.answer_correct) {
        console.log("right answer");
        $("#good_job_msg").fadeIn().delay(800).fadeOut(submitAnswer(answer_info));
    } else {
        console.log("Document has focus? ", document.hasFocus());
        showAnswer();
        console.log("Document has focus? ", document.hasFocus());

        // set 60s timer for wrong answer submission
        timer_id = setTimeout(submitWrongAnswer, 60000, answer_info)

        // add timer id to wrong_answers_log
        wrong_answers_log[answer_info.language].timer_id = timer_id;
        console.log("added timer id: ");
        console.log(wrong_answers_log[answer_info.language].timer_id);
        console.log("button display: ");
        console.log($("#send_answer_btn").css("display"));
        // document loses focus (in Firefox, for example)
        // so set focus to "red button"
        // otherwise pressing enter key does not submit the (wrong) answer
        $("#wrong_answer_btn").focus();
    }
}



function submitAnswer(answer_info) {
    // flag to keep track of if load_question request is for a question in a new language
    $.post("/next-question",
            {
                user_answer : answer_info.user_answer,
                question_id : answer_info.question_id,
                student_id : answer_info.student_id,
                answer_correct : answer_info.answer_correct,
                audio_answer_correct : answer_info.audio_answer_correct,
                language : answer_info.language
            },
            load_question, "json"
    );
    console.log("passed to server student_id: ", answer_info.student_id);
    console.log("passed to server question_id: ", answer_info.question_id);
}

function submitWrongAnswer(answer_info) {
    console.log("deleting from wrong answer log: ");
    console.log(answer_info.user_answer);
    console.log(answer_info.language);
    delete wrong_answers_log[answer_info.language];

    // when submission is delayed, the active language might not be the same
    // as the language of this submission, so check
    if (current_language===answer_info.language) {
        hideAnswer();
    }

    submitAnswer(answer_info);
}

function showAnswer() {
    console.log("about to show wrong answer");
    console.log($("#send_answer_btn"));
    console.log($("#send_answer_btn").css("display"));
    // $("#send_answer_btn").hide();
    $("#send_answer_btn").css("display", "none");
    console.log("hid the submit button");
    console.log($("#send_answer_btn"));
    console.log($("#send_answer_btn").css("display"));
    $("#wrong_answer_btn").fadeIn();
    $("#show_answer").fadeIn();
    $("#gtranslate").fadeIn();
    set_height_img_container();

}

function hideAnswer() {
    console.log("hiding the answer");
    $("#show_answer").hide();
    $("#gtranslate").hide();
    $("#translate_text_output").hide();
    $("#wrong_answer_btn").fadeOut(function(){
        $("#send_answer_btn").css("display", "inline-block");});
    console.log("answer hidden");

}

// callback function for ajax request - loads a new question
function load_question(new_question)  {
    console.log(new_question);
    var quest_obj=new_question;
    repeat_question =  (quest_obj.id === current_ids.question_id);

    // refresh the page with new question, unless it's the same question as current one
    if (! repeat_question ||
        quest_obj.request_type==="GET") {
        // there are a maximum of 4 images per question
        var images = quest_obj.images;
        var images_count = images.length;

        // check how many images previous question had
        var prev_images_count = 1;
        if ($("#picture-4").length) {
            prev_images_count = 4;
        } else if ($("#picture-3").length) {
            prev_images_count = 3;
        } else if ($("#picture-2").length) {
            prev_images_count = 2;
        }

        var images_count_change = images_count - prev_images_count;

        console.log("images_count_change: ", images_count_change);
        console.log("prev_images_count: ", prev_images_count);
        console.log("images_count: ", images_count);

        switch (images_count_change) {
            case -3:
                remove_pictures(prev_images_count, 3);
                console.log("removed 3 pictures");
                break;
            case -2:
                remove_pictures(prev_images_count, 2);
                console.log("removed 2 pictures");
                break;
            case -1:
                remove_pictures(prev_images_count, 1);
                console.log("removed 1 picture");
                break;
            case 0:
                break;
            case 1:
                add_pictures(prev_images_count, 1);
                console.log("added 1 picture");
                break;
            case 2:
                add_pictures(prev_images_count, 2);
                console.log("added 2 pictures");
                break;
            case 3:
                add_pictures(prev_images_count, 3);
                console.log("added 3 pictures");
                break;
        }

        update_pictures(images, images_count);

        // at present, only one audio file (in mp3 format) is presented per question
        $("#audio_src").attr("src", bucket + "audio/" + quest_obj.language.toLowerCase() + "/" + quest_obj.audio[0] + ".mp3");
        // reload the audio source in the audio element; jQuery doesn't implement $().load(), so use JavaScript
        document.getElementById('card_audio').load();

        console.log("Hint contains: ", quest_obj.hint);

        if (quest_obj.hint === "") {
            $("#hint-div").css("display", "none");
            console.log("hiding the hint area");
        } else {
            $("#hint-div").css("display", "inline");
            $("#hint").text(quest_obj.hint);
            console.log("showing the hint area");
        }

        $("#part_of_speech_elem").text(quest_obj.part_of_speech);
        $("#word_elem").text(quest_obj.word);
        $("#user_answer").val("");
        $("#translate_text_input").val(quest_obj.word);
        current_ids.question_id = quest_obj.id;
        console.log("received from server student_id: ", quest_obj.student_id)
        current_ids.student_id = quest_obj.student_id;
        console.log("updated current_ids.student_id to: ", current_ids.student_id)

        // store the answers in a variable
        all_answers = quest_obj.all_answers;
        console.log("answers saved in a variable");

        // prompt temporary user for sign-up after every fifth question answered
        if (quest_obj.prod_signup === true) {
            $("#prod_signup").fadeIn();
            // show the sign-up prompt for 20s, then hide it
            signup_btn_timer_id = setTimeout(function(){$("#prod_signup").fadeOut();},
            20000);
        }
    }

    // if this question was preceded by a question in the same language
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
                $("#send_answer_btn").removeClass("btn-success");
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

    // reset these properties to initial state so that an answer can be
    // submitted again
    enter_pressed=false;
    $("#send_answer_btn").prop("disabled",false);
    $("#user_answer").prop("disabled",false);
    $("#user_answer").focus();
    console.log("finished loading question and reset to defaults");
}

function remove_pictures(last_pic_index, num_pics_to_remove) {
    for (var i=1; i <= num_pics_to_remove; i++) {
        console.log("about to remove element: ", "#picture-" + last_pic_index.toString());
        $("#picture-" + last_pic_index.toString()).remove();
        last_pic_index--;
    }
}

function add_pictures(last_pic_index, num_pics_to_add) {
    for (var i=last_pic_index+1; i <= last_pic_index+num_pics_to_add; i++) {
        var picture_elem = `
            <div id='picture-${i}' class='m-2 align-self-center'>
            <picture>
                <source id='img-webp-${i}'>
                <img id='img-default-${i}' class='rounded mx-auto my-3 d-block img-fluid'>
            </picture>
            </div>
        `;
        $("#images-container").append(picture_elem);
        console.log("added element: ", picture_elem);
    }
}

function update_pictures(images, images_count) {
    for (var i=1; i <= images_count; i++) {
        var file_name = images[i-1][0];
        var file_desc = file_name.split("-").join(" ");
        var _ext = images[i-1][1];
        var img_aspect_ratio = images[i-1][2];
        if (img_aspect_ratio >= 1.333) {
            var width = "480px";
            var height = Math.round(480/img_aspect_ratio).toString();
        } else {
            var width = Math.round(360*img_aspect_ratio).toString();
            var height = "360px";
        }
        var path_f_name = bucket + "pics/" + file_name;
        if (_ext !== "svg")  {
            console.log("updating picture element for: ", _ext);
            console.log("image webp id: ", "#img-webp-" + i.toString());
            // removing previous image before resizing
            // otherwise we see old image resized before the new one loads
            $("#img-webp-" + i.toString()).removeAttr("srcset");
            $("#img-default-" + i.toString()).removeAttr("src");
            $("#img-default-" + i.toString()).removeAttr("srcset");
            $("#img-default-" + i.toString()).css("width", width);
            $("#img-webp-" + i.toString()).attr("srcset", path_f_name + "-480px.webp 1x, " + path_f_name + "-960px.webp 2x");
            $("#img-webp-" + i.toString()).attr("type", "image/webp");
            $("#img-default-" + i.toString()).attr("src", path_f_name + "-480px." + _ext);
            $("#img-default-" + i.toString()).attr("srcset", path_f_name + "-480px." + _ext +" 1x, " + path_f_name + "-960px." + _ext +" 2x");
            $("#img-default-" + i.toString()).attr("alt", file_desc);
        } else if (_ext === "svg") {
            console.log("updating picture element for svg");
            console.log("img webp id: ", "#img-webp-" + i.toString());
            // removing previous image before resizing
            // otherwise we see old image resized before the new one loads
            $("#img-webp-" + i.toString()).removeAttr("srcset");
            $("#img-webp-" + i.toString()).removeAttr("type");
            $("#img-default-" + i.toString()).removeAttr("src");
            $("#img-default-" + i.toString()).removeAttr("srcset");
            $("#img-default-" + i.toString()).css("width", width);
            console.log("img-default: ", "#img-default-" + i.toString());
            console.log("file name: ", path_f_name);
            $("#img-default-" + i.toString()).attr("src", path_f_name + ".svg");
            console.log($("#img-default-" + i.toString()).attr("src"));
            $("#img-default-" + i.toString()).attr("alt", file_desc);
        }
    }
    console.log("updated " + images_count + " picture(s)");
}

function set_height_img_container() {
    var fixed_div_height = $("#bottom-container").outerHeight();
    $(document).ready(function() {
        $("#images-container").css("margin-bottom", fixed_div_height);
    });
}