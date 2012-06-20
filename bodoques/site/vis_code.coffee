
# get url params
get_url_vars = () ->
    vars = {}
    hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&')

    for pair in hashes
        hash = pair.split('=')
        vars[hash[0]] = hash[1]
        
    vars

# we removed the %Z at the end because it's not supported yet by d3
time_format = d3.time.format("%a, %d %b %Y %H:%M:%S")

vars = get_url_vars()

console.log vars

d3.json "/api/dash/#{vars['userId']}", (json) ->

    d3.select('#child_name').text(if json.name then json.name else json.user_id)
    d3.select('#time_left').text(json.time_left)
    d3.select('#time_button').on('click', (e) -> 
        console.log '&'
        url = "/api/time/add/?userId=#{vars['userId']}#{'&'}additionalTime=#{60000 * 10}"
        console.log url
        d3.json url, (response) ->
            console.log response
            d3.select('#time_left').text(Math.round(response.allowedTime / (60 * 1000)))
    )

    console.log json
    window.data = json
    
    bar_width = 18
    bar_height = 15
    bar_sep = 5
    
    # most visited sites
    
    json.sites.forEach (e) -> 
        e.minutes = +e.milliseconds / (1000 * 60)
        console.log e.minutes
    
    vis = d3.select('#vis').append('svg').attr('width', 450).attr('height', (bar_height + bar_sep) * json.sites.length + 40)
    
    width = d3.scale.linear().domain([0, d3.max(json.sites, (e) -> e.minutes)]).range([0, 200])
    
    bars = vis.selectAll('rect')
        .data(json.sites)
        
    bars.enter()
        .append('rect')
        .attr('x', 100)
        .attr('y', (d, i) -> (bar_height + bar_sep) * i)
        .attr('fill', 'steelblue')
        .attr('width', 0)
        .attr('height', bar_height)
        .transition()
        .delay(50)
        .attr('width', (d) -> width(d.minutes))
        
    labels = vis.selectAll('text')
        .data(json.sites)
        
    labels.enter()
        .append('text')
        .text((d) -> d.site__url)
        .attr('font-size', '12px')
        .attr('text-anchor', 'end')
        .attr('dy', '0.37em')
        .attr('x', 97)
        .attr('y', (d, i) -> (bar_height + bar_sep) * i + bar_height / 2.0)
        
    x_axis = d3.svg.axis().scale(width).ticks(2).orient("bottom")
    
    vis.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(#{97}, #{(bar_height + bar_sep) * json.sites.length})")
        .call(x_axis)

    # daily behavior
    
    json.counts.forEach (c) ->
        c.good.sum = +c.good.sum / (60)
        c.bad.sum = +c.bad.sum / (60)
    
    max_height = 150
    vis2 = d3.select('#vis2').append('svg').attr('width', (bar_width + bar_sep) * json.counts.length + 80).attr('height', max_height + 100)
    
    height = d3.scale.linear().domain([0, d3.max(json.counts, (e) -> e.bad.sum + e.good.sum)]).range([max_height, 0])
    
    bad = vis2.selectAll('rect.bad')
        .data(json.counts)
        
    bad.enter()
        .append('rect')
        .attr('class', 'bad')
        .attr('x', (d, i) -> i * (bar_width + bar_sep))
        .attr('y', (d) -> height(d.bad.sum) + 10)
        .attr('width', bar_width)
        .attr('height', (d) -> max_height - height(d.bad.sum))
        .attr('fill', 'darkred')
        
    good = vis2.selectAll('rect.good')
        .data(json.counts)

    good.enter()
        .append('rect')
        .attr('class', 'good')
        .attr('x', (d, i) -> i * (bar_width + bar_sep))
        .attr('y', (d) -> height(d.good.sum + d.bad.sum) + 10)
        .attr('width', bar_width)
        .attr('height', (d) -> max_height - height(d.good.sum))
        .attr('fill', 'steelblue')
        
    labels = vis2.selectAll('g')
        .data(json.counts)
        .enter()
        .append('g')
        .attr('transform', (d, i) -> "translate(#{i * (bar_width + bar_sep) + bar_width / 2}, #{max_height + 15}) rotate(#{60})")
        .selectAll('text')
        .data((d) -> [d])
        .enter()
        .append('text')
        .text((d) -> d.date)
        .attr('font-size', '11px')
        .attr('dy', '0.35em')
        
    vis2.append('line')
        .attr('x1', 0)
        .attr('x2', bar_width * json.counts.length + bar_sep * (json.counts.length - 1))
        .attr('y1', max_height + 10)
        .attr('y2', max_height + 10)
        .attr('stroke', 'black')
        .attr('stroke-width', 1)
        
    y_axis = d3.svg.axis().scale(height).ticks(2).orient("right")
    
    vis2.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(#{(bar_width + bar_sep) * json.counts.length}, #{10})")
        .call(y_axis)
        

    # activity
    d3.select('#last_activity').selectAll('li')
        .data(json.last_activity)
        .enter()
        .append('li')
        .text((d) -> "#{d.date} - #{d.url} - #{d.minutes} minutes")
        
        

'''
d3.xml 'data/signal.rss', (xml) ->
    items = xml.getElementsByTagName('item')
    console.log items
    window.items = (i for i in items)
    window.items = window.items.map (e) ->
        date = e.getElementsByTagName('pubDate')[0].textContent
        date = date.substr(0, date.length - 6)
        {
            date: time_format.parse(date),
            title: e.getElementsByTagName('title')[0].textContent,
            link: e.getElementsByTagName('link')[0].textContent
        }
        
    today = new Date
    start = d3.time.month.offset(today, -1)
    
    console.log window.items.length 
    window.items = window.items.filter (e) -> start <= e.date <= today  
    
    console.log window.items
    
    console.log today
    console.log start
    
    x_scale = d3.time.scale().domain([start, today]).range([0, 950])
    
    circles = vis.selectAll('circle')
        .data(window.items)
        
    circles.enter()
        .append('circle')
            .attr('r', 5)
            .attr('cx', (d) -> x_scale(d.date))
            .attr('cy', 50)
            .attr('fill', 'steelblue')
            .attr('title', (d) -> d.title)
            
    circles.each((d,i) ->
        $(@).tipsy({
            gravity: 'n',
            html: false
        })
    )
'''