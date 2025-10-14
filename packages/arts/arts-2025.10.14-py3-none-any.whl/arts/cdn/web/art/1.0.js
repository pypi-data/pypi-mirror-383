art = {}

art.video_suffixes = ['mp4']
art.img_suffixes = ['jpg', 'png', 'jpeg']
art.audio_suffixes = ['flac', 'mp3', 'ogg']

art.open = (href) => { event.preventDefault(); window.open(href, '_blank') }

art.media_base = (srcs, type) => {
    let script = document.currentScript
    let content = []
    for (let src of srcs) {
        let suffix = src.match(/\.([^.]+)$/)
        if (suffix) {
            suffix = suffix[1]
            if (art.video_suffixes.includes(suffix)) { content.push(`<video loading="lazy" src='${src}' controls href='${src}'></video>`) }
            else if (art.img_suffixes.includes(suffix)) { content.push(`<img loading="lazy" src='${src}' href='${src}'>`) }
            else if (art.audio_suffixes.includes(suffix)) { { content.push(`<audio loading="lazy" controls src="${src}"></audio>`) } }
        }
    }
    if (content) {
        let ele = document.createElement('div')
        ele.classList.add(type)
        ele.innerHTML += content.join('')
        script.parentElement.appendChild(ele)
    }
    script.remove()
}
art.get_static_srcs = (dir) => {
    let srcs = []
    let files = art.meta.static[dir]
    if (files) {  // 在js中, Boolean([])的值为true
        for (let file of files) { srcs.push(`static/${dir}/${file}`) }
    }
    return srcs
}

static = (srcs) => art.media_base(srcs, 'static')
row_static = (srcs) => art.media_base(srcs, 'row_static')

art.clean_text = (text) => {
    text = text.trim()
    text = text.replace(/>\s*/gs, '>')
    text = text.replace(/\s*</gs, '<')
    text = text.replace(/\s*\\\s*\n\s*/gs, '')  // 解析/拼接符
    text = text.replace(/\n +/gs, '\n')  // 去除每行开头的空格
    return text
}

art.code_index = 0
art.codes = {}
code = (code_string, min_height = 17.5) => {
    let script = document.currentScript
    art.code_index += 1
    let code_mark = `<script>\`${Date.now()}_canbiaoxu_com_code_index_${art.code_index}\`</script>`
    script.parentElement.innerHTML += code_mark
    code_string = code_string.replace(/^[^\S\n]*\n?/gs, '').replace(/\n?[^\S\n]*$/gs, '')
    code_string = `<code><textarea style="min-height: ${min_height}rem;">${code_string}</textarea></code>`
    art.codes[code_mark] = code_string
    script.remove()
}
art.unfold_code = (textarea) => { textarea.style.height = textarea.scrollHeight + 25 + 'px' }

art.set_screen_type = () => {
    document.documentElement.setAttribute('screen_type', 'y')  // 检测失败时按竖屏处理
    if (!window.frameElement) {
        let screen_type = screen.orientation.type.includes('landscape') ? 'x' : 'y'
        document.documentElement.setAttribute('screen_type', screen_type)
    }
}

art.render = (mini_title = false, big_title = true, home_link=true) => {
    document.currentScript.remove()
    let text = document.querySelector('body > text')
    for (let row_gap of text.querySelectorAll('row_gap')) {
        let num = row_gap.innerText
        if (num) {
            row_gap.style.height = `${num}rem`
            row_gap.innerText = ''
        }
    }
    let mini_title_text = ''
    let big_title_text = ''
    let innerHTML = text.innerHTML
    let foot_text = ''
    let title = document.title
    if (window.self === window.top) {
        if (title && mini_title) { mini_title_text = `<mini_title>${title}</mini_title>` }
        if (title && big_title) { big_title_text = `<h1>${title}</h1>` }
        if (home_link) {foot_text = `<home_link><button href='/'>主页 👈</button></home_link>`}
    }
    innerHTML = art.clean_text(mini_title_text + big_title_text + innerHTML + foot_text)
    for (let [k, v] of Object.entries(art.codes)) {
        innerHTML = innerHTML.replace(k, v)  // 在js中, replace最多只会替换1次
    }
    text.innerHTML = innerHTML
    for (let ele of document.querySelectorAll('people>img')) {
        ele.classList.add('portrait')
    }
    // 置底
    for (let ele of document.querySelectorAll('code>textarea')) { art.unfold_code(ele) }
    for (let e of document.querySelectorAll('body [href]')) {
        e.addEventListener('click', async () => art.open(e.href || e.getAttribute('href')))
    }
    text.addEventListener('dblclick', async () => art.open(document.URL))
}

{
    const iframe = window.frameElement
    if (iframe) {
        const resizeObserver = new ResizeObserver(entries => {
            iframe.style.height = `${entries[0].contentRect.height}px`
        })
        resizeObserver.observe(document.documentElement)
    }
}

art.set_screen_type()