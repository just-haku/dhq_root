with open("sweep_test.html", "w") as f:
    f.write('<html><body>\n')
    f.write('<h2>Sweep 1 (Large 0)</h2>\n')
    f.write('<svg width="200" height="200"><path d="M 50,100 A 50,50 0 0 1 150,100" fill="none" stroke="black"/></svg>\n')
    f.write('<h2>Sweep 0 (Large 0)</h2>\n')
    f.write('<svg width="200" height="200"><path d="M 50,100 A 50,50 0 0 0 150,100" fill="none" stroke="black"/></svg>\n')
    f.write('</body></html>\n')
