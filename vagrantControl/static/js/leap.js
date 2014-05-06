Leap.loop(function(frame) {
    if (frame.pointables.length > 0) {
        document.body.style.cursor = 'none';
        var position = frame.pointables[0].stabilizedTipPosition;
        var normalized = frame.interactionBox.normalizePoint(position);
        var now = new Date();

        var x = window.innerWidth * normalized[0];
        var y = window.innerHeight * (1 - normalized[1]);
        this.element = document.getElementById('position');

        this.element.style.display = 'block';
        this.element.style.left = x + 'px';
        this.element.style.top = y + 'px';

        if(this.underElement && this.underElement == document.elementFromPoint(x,y)){
            elapsedTime = now.getTime() - this.startedHover;
            if(elapsedTime > 1000){
                this.underElement.click();
                this.underElement.focus();
                $(this.element).addClass('active');
                window.setTimeout(function(){
                    $('#position').removeClass('active');
                },500);
            }
        }else{
            this.underElement = document.elementFromPoint(x,y);
            this.startedHover = now.getTime();
            $('.leap-hover').removeClass('leap-hover');
            if(this.underElement && (this.underElement.nodeName == 'A' || this.underElement.nodeName == 'INPUT')){
                $(this.underElement).addClass('leap-hover');
            }
        }
    } else {
        document.body.style.cursor = 'default';
    }
});

