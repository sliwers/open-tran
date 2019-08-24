function formsubmit(){
        mode = document.search_form.mode.value;

        nhref = "http://"
                + document.search_form.src.value;

        if (mode == "suggest")
                nhref += "."
                        + document.search_form.dst.value;
        
        location.href = nhref
                + ".open-tran.eu/"
                + mode
                + "/"
                + document.search_form.q.value;
        return false;
}

function get_element(id)
{
        if (document.layers)
                return document.layers[id];
        else if (document.all)
                return document.all[id];
        else if (document.getElementById)
                return document.getElementById(id);
        return null;
}

function visibility_switch(id)
{
        elem = get_element(id);
        if (elem != null){
                nstyle = (elem.style.display == 'none') ? 'block' : 'none';
                elem.style.display = nstyle;
        }
}

function mode_enable(elem_name)
{
        elem = get_element(elem_name);
        if (elem){
                elem.style.background = "#fff";
                elem.style.color = "#000";
        }
}

function mode_disable(elem_name)
{
        elem = get_element(elem_name);
        if (elem){
                elem.style.background = "#ecf3f9";
                elem.style.color = "#103c93";
        }
}

function switch_select_indices()
{
        s1 = document.search_form.src;
        s2 = document.search_form.dst;
        tmp = s1.selectedIndex;
        s1.selectedIndex = s2.selectedIndex;
        s2.selectedIndex = tmp;
}

function second_lang_enable()
{
        blinline = document.search_form.src.style.display;
        document.search_form.dst.style.display = blinline;
        get_element('form_lang_switch').style.display = blinline;
}

function second_lang_disable()
{
        document.search_form.dst.style.display = 'none';
        get_element('form_lang_switch').style.display = 'none';
}

function refresh_mode()
{
        mode = document.search_form.mode.value;
        if (mode == "suggest"){
                mode_disable('form_mode_compare');
                mode_enable('form_mode_suggest');
                second_lang_enable();
        }
        else if (mode == "compare"){
                mode_disable('form_mode_suggest');
                mode_enable('form_mode_compare');
                second_lang_disable();
        }
}

function set_mode(mode)
{
        if (document.search_form.mode.value == mode)
                return;
        document.search_form.mode.value = mode;
        document.cookie = "mode=" + mode + "; domain=.open-tran.eu";
        refresh_mode();
}

function get_cookie(name, def)
{
        if (document.cookie.length>0){
                c_start = document.cookie.indexOf(name + "=");
                if (c_start != -1){
                        c_start = c_start + name.length + 1;
                        c_end = document.cookie.indexOf(";", c_start);
                        if (c_end == -1)
                                c_end = document.cookie.length;
                        return unescape(document.cookie.substring(c_start,c_end));
                } 
        }
        return def;
}

function initialize()
{
        document.search_form.mode.value = get_cookie("mode", "suggest");
        refresh_mode();
        document.search_form.q.focus();
        return false;
}
