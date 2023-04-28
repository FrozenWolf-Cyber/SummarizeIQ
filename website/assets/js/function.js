const article_list = document.getElementById("article_list");
const summary_header = document.getElementById("summary_header");

const sort_btn = document.getElementById("sort");

const summary_body = document.getElementById("summary_body");
const search = document.getElementById("search");
const search_box = document.getElementById("search_box");
const search_query_box = document.getElementById("search_query_box");
const keywords = document.getElementById("keywords");

var openai_score = document.getElementsByClassName("openai_score");
var t5_score = document.getElementsByClassName("t5_score");

var active_article = undefined
var sort_by_openai = true
var last_search = search_box.value
// var no_query = true
var searching = false

var last_search_query = search_query_box.value
// var no_query = true
var searching_query = false

var data, data_;
var ranking = {}
// const t5 = document.getElementById("t5");
// const gpt = document.getElementById("gpt");
// const genism = document.getElementById("genism");
// const lsa = document.getElementById("lsa");
// const lex = document.getElementById("lex");
// const luhn = document.getElementById("luhn");

var search_results = {}

var total_summary = {}
var each_summary = {}

var total_keywords = []
var each_keywords = {}


var combined_prompt = ""

var active_model = document.getElementsByClassName("algo nav-link active")[0]

summary_header.innerText = active_model.id + " summary"

const algo = document.getElementsByClassName("algo")

for (var i=0; i<algo.length; i++){
    const each_algo = algo[i]

    each_algo.addEventListener("click", async function() { 
        if (active_article!=undefined){
            active_article.className = "card"
        }

        active_article = undefined

        if (total_summary[each_algo.id] != undefined){
            summary_body.innerText = total_summary[each_algo.id]
            keywords.innerText = total_keywords[each_algo.id]
            summary_header.innerText = document.getElementsByClassName("algo nav-link active")[0].id + ' Summary'
        }
        
        else{
            summary_body.innerText = "Generating summary..."
            keywords.innerText = "Generating keyword..."
            
            summary = undefined
            if (each_algo.id == "openai" || each_algo.id == "t5"){
                var articles = article_list.children
                var new_prompt = ""

                for (var i=0; i<articles.length; i++){
                    var box2 = articles[i].children[0].children[0]
                    
                    if (each_summary[box2.innerText] != undefined){
                        if (each_summary[box2.innerText]["lex"]!= undefined){
                            new_prompt +=  "\n\n\n" + each_summary[box2.innerText]["lex"]
                            continue
                        }
                    }
                
                    data_ = await get_summary_for("lex", search_results[box2.innerText][0])
                    each_keywords[box2.innerText] = data_.keywords
                    each_summary[box2.innerText] = {}
                    Object.entries(data_).forEach(([key, value]) => {
                        if (key!="keywords"){
                            each_summary[box2.innerText]["lex"] = value
                            new_prompt +=  "\n\n\n" + each_summary[box2.innerText]["lex"]
                        }
                     });
                    }

                summary = await get_summary_for(each_algo.id, new_prompt)

            }
            else{
                summary = await get_summary_for(each_algo.id, combined_prompt)
            }
            // console.log(each_algo.id, summary, summary[each_algo.id])
            total_summary[each_algo.id] = summary[each_algo.id]
            summary_body.innerText = total_summary[each_algo.id]
            summary_header.innerText = document.getElementsByClassName("algo nav-link active")[0].id + ' Summary'
            total_keywords[each_algo.id] = summary['keywords']
            keywords.innerText = summary['keywords']
        }

    });
}


// function custom_sort(dict, i){
//     var list = dict.keys()
//     var keys = dict.value()
//     var temp

//     flags=0
//     for (var i=0; i<list.length; i++){
//         for (var j=0; j<list.length-1; j++){
//             if (keys[j][i]>keys[j+1][i]){
//                 temp = keys[j]
//                 keys[j] = keys[j+1]
//                 keys[j+1] = temp

//                 temp = list[j]
//                 list[j] = list[j+1]
//                 list[j+1] = temp

//                 flag = 1
//             }
//         }

//         if (flag ==0){
//             break
//         }
//     }

//     return list
// }

// function sort_by(){
//     if (sort_by_openai){
//         sort_by_openai = false
        
//         sorted = custom_sort(ranking, 1)
        
//         var oldlist = article_list.children

//         article_list.children = []

//         for (var i =0; i<sorted.length; i++){
//             for (var j =0; j<sorted.length; j++){
//                 if (oldlist[j].children[1])
//             }
//         }

        
//     }
//     else{
//         sort_by_openai = true
//     }
// }

async function search_prompt() { 
    if (last_search != search_box.value && searching==false){
        searching = true
        console.log("searching... "+search_box.value)
        const response = await fetch('http://127.0.0.1:5000/search', {
            method: "POST",
            headers: {"content-type": "application/json"},
            body: JSON.stringify({ prompt: search_box.value }),
        })
        
        data= await response.json();
        console.log(data);

        searching = false
        last_search = search_box.value
        
        total_summary = {}
        each_summary = {}
        each_article_embed = {}

        number_articles = 0
        while (article_list.firstChild) {
            article_list.removeChild(article_list.firstChild);
        }
        
        set_search_result(data)
        

        active_model = document.getElementsByClassName("algo nav-link active")[0]


        active_model.click()
    }

    else{
        alert("ALREADY SHOWING RESULTS FOR GIVEN SEARCH OR SEARCH IN PROGRESS!!")
    }
        
};


async function search_query() { 
    if (last_search_query != search_query_box.value && searching_query==false){
        searching_query = true
        console.log("searching... "+search_query_box.value)
        const response = await fetch('http://127.0.0.1:5000/get_scores', {
            method: "POST",
            headers: {"content-type": "application/json"},
            body: JSON.stringify({ query: search_query_box.value, results: search_results }),
        })
        
        data= await response.json();
        console.log(data);

        searching_query = false
        last_search_query = search_query_box.value
        
        ranking = data

        openai_score = document.getElementsByClassName("openai_score");
        t5_score = document.getElementsByClassName("t5_score");

        Object.entries(ranking).forEach(([key, value]) => {
            for (var i=0; i<openai_score.length; i++){
                if (key == openai_score[i].id.replace("openai","")){
                    openai_score[i].innerText = "Openai Score: "+ (value[0]*100).toFixed(2);
                }
                if (key == t5_score[i].id.replace("t5","")){
                    t5_score[i].innerText = "T5 Score: "+ (value[1]*100).toFixed(2);

                }
            }
            
         });

    }

    else{
        alert("ALREADY SHOWING RESULTS FOR GIVEN SEARCH OR SEARCH IN PROGRESS!!")
    }
        
};



function set_search_result(results){
    search_results = results

    Object.entries(results).forEach(([key, value]) => {
        create_article(key, value[0], value[1])
        
     });

     search_results = results
     combined_prompt = ""

     Object.entries(search_results).forEach(([key, value]) => {
        combined_prompt = combined_prompt + "\n\n\n" + value[0]
     });
     
}

async function get_summary_for(this_model, prompt){
    searching = true
    console.log("searching... "+search_box.value)
    const response = await fetch('http://127.0.0.1:5000/get_summary', {
        method: "POST",
        headers: {"content-type": "application/json"},
        body: JSON.stringify({ model: this_model, prompt: prompt }),
    })
    
    data= await response.json();
    searching = false
    console.log(data);
    return await data
}





var number_articles = 0

function create_article(title, desc, link){

    const box = document.createElement("div");
    box.className = "card"
    article_list.appendChild(box);

    const box1 = document.createElement("div");
    box1.className = "card-body"



    box.appendChild(box1);

    const box2 = document.createElement("h4");
    box2.className = "card-title"
    box2.id = "articletitle"+number_articles;
    box2.innerText = title
    box1.appendChild(box2);

    const box3 = document.createElement("p");
    box3.className = "card-text"
    box3.id = "articlebody"+number_articles;
    box3.innerText = desc.replaceAll("\n","").substring(0,200)+'....'
    box3.style.overflowY = "hidden"
    box3.style.overflowX = "hidden"

    
    
    box.addEventListener("click", async function() { 
        active_model = document.getElementsByClassName("algo nav-link active")[0]

        if (active_article!=undefined){
            active_article.className = "card"
        }


        active_article = box
        box.className = "card selected_card"

        if (each_summary[box2.innerText] != undefined){
            if (each_summary[box2.innerText][active_model.id]!= undefined){
                summary_body.innerText = each_summary[box2.innerText][active_model.id]
                keywords.innerText = each_keywords[box2.innerText]
                return
            }
        }
   
        summary_body.innerText = "Generating summary..."
        keywords.innerText = "Generating keyword..."
        console.log("REQUESTING SUMMARY USING THESE:   ",active_model.id, search_results[box2.innerText][0])
        data_ = await get_summary_for(active_model.id, search_results[box2.innerText][0])
        each_keywords[box2.innerText] = data_.keywords
        each_summary[box2.innerText] = {}
        Object.entries(data_).forEach(([key, value]) => {
            if (key!="keywords"){
                each_summary[box2.innerText][active_model.id] = value
                summary_body.innerText = value
                keywords.innerText = each_keywords[box2.innerText]
            }
         });

            


    });
        

    box1.appendChild(box3);

    const box4 = document.createElement("a");
    box4.className = "card-link"
    box4.id = "articlelink"+number_articles;
    box4.innerText = "Link"
    box4.href = link
    box1.appendChild(box4);

    const bold = document.createElement("b");
    const openai_score_create = document.createElement("a");
    openai_score_create.className = "openai_score card-body"
    openai_score_create.id = "openai"+title
    openai_score_create.innerText = "Openai Score: "

    const t5_score_create = document.createElement("a");
    t5_score_create.className = "t5_score card-body"
    t5_score_create.id = "t5"+title
    t5_score_create.innerText = "T5 Score: "

    bold.appendChild(openai_score_create);
    bold.appendChild(t5_score_create);

    box1.appendChild(bold)

    number_articles++;

    return [box2, box3, box4]

}
