var testEditor;

$(function () {

    $.get("{% static 'editor/notes/empty.md' %}", function (md) {
        // console.log(md);
        testEditor = editormd("test-editormd", {
            width: "100%",
            height: 1100,
            path: "{% static 'editor/lib/' %}",
            theme: "dark",
            previewTheme: "dark",
            editorTheme: "pastel-on-dark",
            markdown: md,
            codeFold: true,
            //syncScrolling : false,
            saveHTMLToTextarea: true,    // 保存 HTML 到 Textarea
            searchReplace: true,
            //watch : false,                // 关闭实时预览
            htmlDecode: "style,script,iframe|on*",            // 开启 HTML 标签解析，为了安全性，默认不开启    
            // toolbar  : false,             //关闭工具栏
            //previewCodeHighlight : false, // 关闭预览 HTML 的代码块高亮，默认开启
            emoji: true,
            taskList: true,
            tocm: true,         // Using [TOCM]
            tex: true,                   // 开启科学公式TeX语言支持，默认关闭
            flowChart: true,             // 开启流程图支持，默认关闭
            sequenceDiagram: true,       // 开启时序/序列图支持，默认关闭,
            //dialogLockScreen : false,   // 设置弹出层对话框不锁屏，全局通用，默认为true
            //dialogShowMask : false,     // 设置弹出层对话框显示透明遮罩层，全局通用，默认为true
            //dialogDraggable : false,    // 设置弹出层对话框不可拖动，全局通用，默认为true
            //dialogMaskOpacity : 0.4,    // 设置透明遮罩层的透明度，全局通用，默认值为0.1
            //dialogMaskBgColor : "#000", // 设置透明遮罩层的背景颜色，全局通用，默认为#fff
            imageUpload: true,
            imageFormats: ["jpg", "jpeg", "gif", "png", "bmp", "webp"],
            imageUploadURL: "./php/upload.php",
            onload: function () {
                console.log('onload', this);
                //this.fullscreen();
                //this.unwatch();
                //this.watch().fullscreen();

                //this.setMarkdown("#PHP");
                //this.width("100%");
                //this.height(480);
                //this.resize("100%", 640);
            }
        });
    });
    /* note-list.json is loaded here */
    function load_note_list() {
        $("#note_list ul").empty();
        $.get("{% static 'editor/json/note-list.json' %}", function (json) {
            console.log(json.notes.length);
            for (var i = 0; i < json.notes.length; i++) {
                console.log(i);
                $("#note_list ul").append('<li><a href="#">' + json.notes[i].title + '</a></li>');
            }
            $('#note_list a').addClass("w3-bar-item w3-button");
            $('#note_list ul').children().click(function () {
                var path = json.notes[$(this).index()].path;
                var title = json.notes[$(this).index()].title;
                console.log(title);
                $.get(path, function (md) {
                    $("#note-title").val(title);
                    testEditor.load_note(md);
                });
            });
        });
    }

    function load_default() {
        $("#note-title").val("");
        testEditor.clear();
    }


    $("#new-btn").bind('click', function () {
        load_default();
    })

    $("#delete-btn").bind('click', function () {
        if ($("#note-title").val() == "") {
            alert("Please specify the note you want to delete");
        } else {
            $.ajax({
                method: 'POST',
                url: "{% url 'editor:delete_note' %}",
                data: {
                    fname: $("#note-title").val() + ".md",
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function () {
                    alert('Note deleted');
                    load_note_list();
                    load_default();
                },
            });
        }
    });

    $("#export-btn").bind('click', function () {
        testEditor.save_note();
    });

    $("#save-btn").bind('click', function () {
        console.log($("#note-title").val())
        if ($("#note-title").val() == "") {
            alert("Please give your note a title");
        } else {
            $.ajax({
                method: 'POST',
                url: "{% url 'editor:save_note' %}",
                data: {
                    md: testEditor.getMarkdown(),
                    fname: $("#note-title").val() + ".md",
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function () {
                    load_default();
                    alert('Note saved');
                    load_note_list();
                },
            });
        }

    });

    $("#import-btn").bind('click', function () {
        var files = document.getElementById('import-btn');
        files.addEventListener('change', function (event) {
            console.log(event.target.files);
            console.log(
                `文件名称:${event.target.files[0].name}
                            文件类型:${event.target.files[0].type}
                            文件大小:${event.target.files[0].size} bytes`
            );


            let file = event.target.files[0];
            let reader = new FileReader();
            reader.readAsText(file);
            reader.onload = function () {
                console.log(reader.result);
                testEditor.load_note(reader.result);
            }
        });
    });

    $("#preview-btn").bind('click', function () {
        testEditor.previewing();
    });

    var flag = 1;
    $("#toggle-toolbar-btn").bind('click', function () {
        if (flag == 0) {
            testEditor.showToolbar();
            flag = 1;
        } else {
            testEditor.hideToolbar();
            flag = 0;
        }
    });
    load_note_list();

    // Read LocalStorage Data
    function getData() {
        var data = localStorage.getItem("notelist");
        if (data !== null) {
            // 本地存储里面的数据是字符串格式的 但是我们需要的是对象格式的
            return JSON.parse(data);
        } else {
            return [];
        }
    }

    // Save LocalStorage Data
    function saveData(data) {
        localStorage.setItem("notelist", JSON.stringify(data));
    }

    // load and render the sidebar note list
    // 渲染加载数据
    function load() {
        // 读取本地存储的数据
        var data = getData();
        console.log(data);
        // clear the original elements in the note-list
        $("#note_list ul").empty();

        $.get("{% static 'editor/json/note-list.json' %}", function (json) {
            console.log(json.notes.length);
            saveData(json);
            // $.each(json.notes, function(i, n){
            //     $("#note_list ul").append('<li><p>' + n.title + '</p> <a href="javascript:;" id=' + i + '></a></li>');
            // });
            // $('#note_list a').addClass("w3-bar-item w3-button");
            // $('#note_list ul').children().click(function () {
            //     var path = json.notes[$(this).index()].path;
            //     var title = json.notes[$(this).index()].title;
            //     console.log(title);
            //     $.get(path, function (md) {
            //         $("#note-title").val(title);
            //         testEditor.load_note(md);
            //     });
            // });
        });
    }
});