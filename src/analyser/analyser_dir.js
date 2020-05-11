urldir = null;
files = [];
record_names = [];

function display_selected(file_id) {
    console.log(file_id);
    console.log(this);
    console.log(document.getElementById("li" + file_id));
    $.get(urldir + "/" + file_id + ".txt", data => {
        // console.log(data);
        record = data;
        process_text();
        render(current = 0);
    })
}

function build_record_list(data) {
    var splited = data.replace(/\r/g, '');
    splited = splited.split("\n").slice(2);
    var filelist = $("#file-list");
    filelist.empty();
    try {
        splited.forEach(element => {
            if (element[0] != "=") {
                var file_id = element.split(" ")[1];
                filelist.append("<li onclick='display_selected(\"" + file_id + "\");' id='li" + file_id + "'>" + element + "</li>");
                record_names.push(urldir + "/" + file_id + ".txt");
            } else {
                throw error;
            }
        })
    } catch (error) {
        // 只是用来跳出forEach
    }
    console.log(record_names);
}

function on_get_url(event) {
    urldir = document.getElementById("urldir").value;
    if (urldir == null) {
        alert("请填写url");
        return;
    }
    if (urldir.slice(0, 4) != "http") {
        urldir = "http://" + urldir;
    }
    if (urldir.indexOf("/_.txt") != -1) {
        alert("不用在url中加入_.txt(给出比赛记录文件夹的url即可)");
    }
    console.log(urldir);
    $("#dir-holder").load(urldir, null, function (response, status, xhr) {
        try {
            var has_ = false;
            var holder = document.getElementById("dir-holder");
            files = Array.from(holder.getElementsByTagName("ul")[0].getElementsByTagName("li"));
            files.forEach(element => {
                if (element.innerText == "_.txt") {
                    $.get(urldir + "/_.txt", build_record_list);
                    has_ = true;
                }
            });
            if (!has_) {
                throw error;
            }
        } catch (error) {
            console.log(holder);
            console.log(files)
            alert("可能不是一个有效的url");
        }
    });
}
