<template>
  <div id="app">
      <div id="ok"/>

    <transition name="fade">
      <div class="query" v-if="presearch">
        <v-icon name="search"></v-icon>
        <input ref="q" v-model="query" type="text" placeholder="create context" @keypress.enter="search"/>
      </div>

      <div class="results" v-else>
          <h1>{{this.query}} </h1>
          <p> {{this.summary}} </p>

          <div class="conf">
              <button> <v-icon name="grid"></v-icon> nodes <input type="text" v-model="layers" @keypress.enter="recreate"/></button>
              <button> <v-icon name="box"></v-icon> depth <input type="text" v-model="depth" @keypress.enter="recreate"/></button>
              <v-icon class="loader" name="loader" v-if="netloading"/>
              <!--<button> <v-icon name="file-plus"></v-icon> data <input type="file" @change="addContext" webkitdirectory directory class="ontp" multiple> </button>-->
              <!--<button> <v-icon name="file-plus"></v-icon> sources </button>-->
          </div>
          <p> {{docs}} documents processed </p>

         <file-upload
          class="uload"
          :extensions="extensions"
          :accept="accept"
          :multiple="multiple"
          :directory="directory"
          :size="0"
          :drop="drop"
          :drop-directory="dropDirectory"
          :add-index="addIndex"
          v-model="files"
          ref="upload"
          >
          <transition name="fade">
              <div v-if="$refs.upload && $refs.upload.dropActive" class="upload">
                    <v-icon name="upload-cloud"/>
                    drop to upload
              </div>
          </transition>

        </file-upload>
          <div class="answer" >
              <div v-for="(a, i) in answers.slice().reverse()" class="card" :key="i">
                  <b>
                      Q: {{a.question}}
                  </b>
                  <p>
                      A: {{a.answer}}
                  </p>
              </div>
          </div>
          <div class="question">
              <input ref="ask" v-model="question" type="text" :placeholder="`query your ${query} net`" @keypress.enter="ask"/>
              <button @click="ask"> <v-icon name="send"></v-icon> </button>
          </div>
      </div>
    </transition>

    <transition name="fade">
    </transition>
  </div>
</template>

<script>

import FileUpload from 'vue-upload-component'
import smoothReflow from 'vue-smooth-reflow'

export default {
  name: 'App',

  components: {
    FileUpload,
  },

  mixins: [smoothReflow],

  data: function(){
      return {
          query: '',
          docs: 1,
          netloading: false,
          threads: 1,
          depth: 1,
          layers: 1,
          presearch: true,
          question: '',
          answers: [],
          summary: '',
          files: [],
          accept: '*',
          multiple: true,
          directory: false,
          drop: true,
          dropDirectory: true,
          addIndex: false,
          thread: 3,
          name: 'file',
          extensions: 'gif,jpg,jpeg,png,webp,pdf,mp3,wav,pptx,doc,docx,txt,csv',
      }
  },

  watch:{
      files: function(){
          console.log(this.$refs.upload.files)
        this.$refs.upload.files.forEach((x) => {
            var data = new FormData()
            data.append('file', x.file)
            this.docs = this.docs + 1
            fetch('http://127.0.0.1:5000/upload', {method: 'POST', body: data }).then((response) => response.json()).then((res) => {
                console.log(res)
            })
        })
        //this.files = []
      }
  },
  methods: {
    jsTransitionScale: function(width, height, speed) {
        var FPS = 60;

        var original_width = 500
        var original_height = 115

        var width_range = width - original_width,
            height_range = height - original_height;

        var timeout = speed / FPS,
            width_change = width_range / FPS,
            height_change = height_range / FPS;

        var finish = new Date().getTime() + speed;

        var begin = setInterval(function () {
            original_width += width_change;
            original_height += height_change;

            window.resizeTo(original_width, original_height)
            if (new Date().getTime() >= finish) {
                window.resizeTo(width, height)
                clearInterval(begin);
            }
        }, timeout);
    },
      addContext:function(event){
        console.log(event.target.files[0].webkitRelativePath)
      },

      recreate: function(){
        this.netloading = true
        fetch('http://127.0.0.1:5000/recreate', {method: 'POST', mode: 'cors', headers: new Headers({ 'Content-Type': 'application/json' }), body: JSON.stringify({ query: this.query, threads: parseInt(this.threads), depth: parseInt(this.depth), layers: parseInt(this.layers) }) }).then((response) => response.json()).then((res) => {
            this.netloading = false
            this.docs = res.docs
        })
      },
      ask: function(){
        fetch('http://127.0.0.1:5000/ask', {method: 'POST', mode: 'cors', headers: new Headers({ 'Content-Type': 'application/json' }), body: JSON.stringify({ question: this.question }) }).then((response) => response.json()).then((res) => {
            this.answers.push({
                answer: res.answer[0][0],
                question: res.question
            })
        })

        this.question = ''
      },

      search: function(){
        fetch('http://127.0.0.1:5000/', {method: 'POST', mode: 'cors', headers: new Headers({ 'Content-Type': 'application/json' }), body: JSON.stringify({ query: this.query }) }).then((response) => response.json()).then((res) => {
            this.jsTransitionScale(500, 415, 500)
            this.summary = res.summary
            this.presearch = false
            this.$nextTick(() => { this.$refs.ask.focus() })
        })
      }
  },

  mounted: function(){
      this.$smoothReflow()

      window.scrollTo(0, 0)
      window.resizeTo(500, 115)

      this.$nextTick(() => {
            this.$refs.q.focus()
            window.VANTA.GLOBE({
              el: "#ok",
              mouseControls: true,
              touchControls: true,
              minHeight: 200.00,
              minWidth: 200.00,
              scale: 1.00,
              scaleMobile: 1.00,
              color: 0x0,
              size: 0.50,
              backgroundColor: 0xffffff
            })

      })
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;700&display=swap');
html, body{
    width: 100vw;
    height: 100vh;
    overflow: hidden;
}
#app {
  font-family: 'Source Sans Pro', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
#ok{
    position: absolute;
    top: 0;
    left: 0;
    width: 150vw;
    height: 150vh;
    z-index: 1;
}

.query{
    position: absolute;
    width: 100%;
    height: 100%;
    top: 5px;
    left: 0;
    z-index: 3;
    display: flex;
    align-items: center;
}

.query input{
    border: none;
    padding: 10px;
    padding-left: 0px;
    border-radius: 5px;
    background-color: rgba(255,255,255, 0.4);
    width: 60vw;
    outline: none;
}
.query svg{
    color: black;
    opacity: 0.3;
    margin: 0 25px;
    width: 20px;
}
.results{
    position: absolute;
    top: 0;
    left: 0;
    padding: 10px 30px;
    width: 100%;
    height: 100%;
    z-index: 3;
}

.results .conf {
    position: relative;
    display: flex;
    padding-top: 10px;
}

.results .conf button svg{
    width: 15px;
    margin-right: 5px;
    vertical-align: middle;
}

@keyframes spin { 100% { -webkit-transform: rotate(360deg); transform:rotate(360deg); } }

.results .conf .loader{
    position: absolute;
    top: 15px;
    right: calc(50% - 10px);
    width: 20px;
    color: black;
    animation:spin 4s linear infinite;
}

.results .conf button{
    position: relative;
    border: none;
    margin-right: 20px;
    padding: 5px 10px;
    border-radius: 5px;
    background-color: rgba(255,255,255, 0.4);
    box-shadow:  24px 24px 48px #d9d9d9, -24px -24px 48px #ffffff;
    cursor: pointer;
    vertical-align: middle;
}


.results .conf button input{
    border: none;
    width: 20px;
    background: transparent;
    text-align: center;
    border-bottom: 1px solid black;
}
.results .conf button .ontp{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    opacity: 0;
    pointer-events: all;
    cursor: pointer;
}

.results p{
    width: 80%;
    text-align: left;
}

.results h1{
    text-align: left;
    color: black;
    margin-top: 35px;
    font-weight: 100;
    letter-spacing: 6px;
    text-transform: uppercase;
}

.question{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100vw;
    display: flex;
    vertical-align: center;
    vertical-align: middle;
    background-color: rgba(255,255,255, 0.4);
    border-radius: 5px;
    z-index: 6;
}

.question input{
    border: none;
    vertical-align: middle;
    outline: none;
    width: 80vw;
    padding: 20px;
}

.question  button{
    border: none;
    cursor: pointer;
    width: 20vw;
    vertical-align: middle;
}

.question button svg{
    width: 20px;
    vertical-align: middle;
    color: black;
}

.answer{
    position: absolute;
    width: calc(100vw - 80px);
    text-transform: capitalize;
    height: auto;
    bottom: 70px;
    z-index: 9;
    padding: 0 40px;
    color: black;
    left: 0;
    display: flex;
    flex-direction: row;
    overflow-x: scroll;
    flex-wrap: nowrap;
}

.answer::-webkit-scrollbar{
    display: none;
}

.card{
    font-size: 9pt;
    border-radius: 5px;
    min-width: 165px;
    width: 200px;
    height: auto;
    margin: 0 10px;
    padding: 10px;
    background-color: rgba(225,225,225,0.4);
    background-filter: blur(3px);
    text-align: left;
}

.upload{
    position: fixed;
    width: 100vw;
    height: 100vh;
    top: 0;
    left: 0;
    z-index: 99;
    pointer-events: none;
    background-color: white;
    opacity: 0.8;
    background-filter: blur(3px);
}
.upload svg{
    display: block;
    width: 20px;
    padding-top: 45vh;
    margin: 0 auto;
    margin-bottom: 10px;
}
.fade-enter-active, .fade-leave-active {
    transition: all 500ms cubic-bezier(0.770, 0.000, 0.175, 1.000); /* easeInOutQuart */
}
.fade-enter, .fade-leave-to {
  opacity: 0;
    transition: all 500ms cubic-bezier(0.770, 0.000, 0.175, 1.000); /* easeInOutQuart */
}
</style>
