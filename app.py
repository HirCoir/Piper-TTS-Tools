<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="keywords" content="texto a voz, TTS, accesibilidad, productividad, herramientas de voz, HirLab, texto a voz, conversión de texto a voz, IA, Hircoir, herramienta de texto a voz, tts.hircoir.eu.org youtube.com/@hircoir, piper, free tts, free text to voice, convertir texto a voz gratis, free ai tts, texto a voz realista, tts realista, free tts, hircoir.eu.org, convertir texto a voz, hircoir project, https://github.com/HirCoir/Piper-TTS-Tools, como convertir texto a voz, text to spech, spech, de texto a voz, hircoir.site, www.hircoir.site, hircoir ai, hircoir IA">
    <meta name="author" content="HirCoir">
    <meta property="og:title" content="TTS Hircoir - Plataforma de Texto a Voz">
    <meta property="og:description" content="Transforma texto en voz GRATIS usando IA">
    <meta property="og:url" content="https://tts.hircoir.eu.org">
    <meta property="og:image" content="https://tts.hircoir.eu.org/og-image.jpg">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="https://tts.hircoir.eu.org">
    <link rel="icon" type="image/x-icon" href="{{ url_for('favicon') }}">
    <title>TTS Hircoir - Plataforma de Texto a Voz</title>
    <script src="https://cdn.altcha.org/altcha.js"></script>
    <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script> <!-- FontAwesome CDN -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #222;
            color: #fff;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .container {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        #audio-container {
            margin-top: 20px;
        }
        footer {
            background-color: #333;
            color: #eee;
            padding: 10px 0;
            text-align: center;
        }
        .icon {
            margin: 0 10px;
            color: #eee;
            transition: color 0.3s;
        }
        .icon:hover {
            color: #fff;
        }
    </style>
</head>
<body>
    <div class="container mx-auto py-10 px-4 md:px-0">
        <h1 class="text-4xl font-bold mb-8">Convertidor de Texto a Audio</h1>
        <form id="conversion-form" class="space-y-4">
            <div>
                <label for="model" class="block text-lg">Modelo:</label>
                <select id="model" name="model" class="w-full p-2 bg-gray-700 border border-gray-600 rounded">
                    {% for model in model_options %}
                    <option value="{{ model }}">{{ model }}</option>
                    {% endfor %}
                </select>
            </div>
            <div>
                <label for="text" class="block text-lg">Texto:</label>
                <textarea id="text" name="text" rows="4" maxlength="1000" placeholder="Escribe tu texto aquí." class="w-full p-2 bg-gray-700 border border-gray-600 rounded autosize"></textarea>
            </div>
            <div id="altcha-container"></div> <!-- Altcha container -->
            <input type="hidden" id="altcha-token" name="altcha_token"> <!-- Hidden field to store Altcha token -->
            <div>
                <button type="submit" class="w-full p-3 bg-blue-600 hover:bg-blue-700 rounded text-white">Generar audio</button>
            </div>
        </form>
        <div id="audio-container" class="mt-8"></div>
    </div>
    <footer>
        <p>© 2024 HirLab. Todos los derechos reservados.</p>
        <div class="flex justify-center mt-4">
            <a href="https://www.youtube.com/@hircoir" class="icon" target="_blank"><i class="fab fa-youtube"></i></a>
            <a href="https://github.com/HirCoir/Piper-TTS-Tools" class="icon" target="_blank"><i class="fab fa-github"></i></a>
        </div>
    </footer>
    <script>
      document.addEventListener('DOMContentLoaded', function() {
        ALTCHA.init({
            hostname: 'tts.hircoir.site',
            apiKey: 'ckey_01e2ba12f3e0bf3cd6530166f491',
            container: 'altcha-container',
            onSuccess: function(token) {
                document.getElementById('altcha-token').value = token;
            }
        });
    });
    </script>
    <script>
        /*!
        autosize 4.0.2
        license: MIT
        http://www.jacklmoore.com/autosize
        */
        !function(e,t){if("function"==typeof define&&define.amd)define(["module","exports"],t);else if("undefined"!=typeof exports)t(module,exports);else{var n={exports:{}};t(n,n.exports),e.autosize=n.exports}}(this,function(e,t){"use strict";var n,o,p="function"==typeof Map?new Map:(n=[],o=[],{has:function(e){return-1<n.indexOf(e)},get:function(e){return o[n.indexOf(e)]},set:function(e,t){-1===n.indexOf(e)&&(n.push(e),o.push(t))},delete:function(e){var t=n.indexOf(e);-1<t&&(n.splice(t,1),o.splice(t,1))}}),c=function(e){return new Event(e,{bubbles:!0})};try{new Event("test")}catch(e){c=function(e){var t=document.createEvent("Event");return t.initEvent(e,!0,!1),t}}function r(r){if(r&&r.nodeName&&"TEXTAREA"===r.nodeName&&!p.has(r)){var e,n=null,o=null,i=null,d=function(){r.clientWidth!==o&&a()},l=function(t){window.removeEventListener("resize",d,!1),r.removeEventListener("input",a,!1),r.removeEventListener("keyup",a,!1),r.removeEventListener("autosize:destroy",l,!1),r.removeEventListener("autosize:update",a,!1),Object.keys(t).forEach(function(e){r.style[e]=t[e]}),p.delete(r)}.bind(r,{height:r.style.height,resize:r.style.resize,overflowY:r.style.overflowY,overflowX:r.style.overflowX,wordWrap:r.style.wordWrap});r.addEventListener("autosize:destroy",l,!1),"onpropertychange"in r&&"oninput"in r&&r.addEventListener("keyup",a,!1),window.addEventListener("resize",d,!1),r.addEventListener("input",a,!1),r.addEventListener("autosize:update",a,!1),r.style.overflowX="hidden",r.style.wordWrap="break-word",p.set(r,{destroy:l,update:a}),"vertical"===(e=window.getComputedStyle(r,null)).resize?r.style.resize="none":"both"===e.resize&&(r.style.resize="horizontal"),n="content-box"===e.boxSizing?-(parseFloat(e.paddingTop)+parseFloat(e.paddingBottom)):parseFloat(e.borderTopWidth)+parseFloat(e.borderBottomWidth),isNaN(n)&&(n=0),a()}function s(e){var t=r.style.width;r.style.width="0px",r.offsetWidth,r.style.width=t,r.style.overflowY=e}function u(){if(0!==r.scrollHeight){var e=function(e){for(var t=[];e&&e.parentNode&&e.parentNode instanceof Element;)e.parentNode.scrollTop&&t.push({node:e.parentNode,scrollTop:e.parentNode.scrollTop}),e=e.parentNode;return t}(r),t=document.documentElement&&document.documentElement.scrollTop;r.style.height="",r.style.height=r.scrollHeight+n+"px",o=r.clientWidth,e.forEach(function(e){e.node.scrollTop=e.scrollTop}),t&&(document.documentElement.scrollTop=t)}}function a(){u();var e=Math.round(parseFloat(r.style.height)),t=window.getComputedStyle(r,null),n="content-box"===t.boxSizing?Math.round(parseFloat(t.height)):r.offsetHeight;if(n<e?"hidden"===t.overflowY&&(s("scroll"),u(),n="content-box"===t.boxSizing?Math.round(parseFloat(window.getComputedStyle(r,null).height)):r.offsetHeight):"hidden"!==t.overflowY&&(s("hidden"),u(),n="content-box"===t.boxSizing?Math.round(parseFloat(window.getComputedStyle(r,null).height)):r.offsetHeight),i!==n){i=n;var o=c("autosize:resized");try{r.dispatchEvent(o)}catch(e){}}}}function i(e){var t=p.get(e);t&&t.destroy()}function d(e){var t=p.get(e);t&&t.update()}var l=null;"undefined"==typeof window||"function"!=typeof window.getComputedStyle?((l=function(e){return e}).destroy=function(e){return e},l.update=function(e){return e}):((l=function(e,t){return e&&Array.prototype.forEach.call(e.length?e:[e],function(e){return r(e)}),e}).destroy=function(e){return e&&Array.prototype.forEach.call(e.length?e:[e],i),e},l.update=function(e){return e&&Array.prototype.forEach.call(e.length?e:[e],d),e}),t.default=l,e.exports=t.default});
    </script>
    <script>
        document.getElementById('conversion-form').addEventListener('submit', async function (e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData
                });
                if (response.ok) {
                    const data = await response.json();
                    const audioContent = data.audio_base64;
                    const audioElement = document.createElement('audio');
                    audioElement.src = 'data:audio/wav;base64,' + audioContent;
                    audioElement.controls = true;
                    audioElement.autoplay = true;
                    document.getElementById('audio-container').innerHTML = '';
                    document.getElementById('audio-container').appendChild(audioElement);
                } else {
                    console.error('Error al convertir texto a voz:', response.statusText);
                }
            } catch (error) {
                console.error('Error de red:', error);
            }
        });

        autosize(document.querySelectorAll('.autosize'));
    </script>
</body>
</html>
