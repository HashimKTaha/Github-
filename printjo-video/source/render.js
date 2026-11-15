const {chromium}=require('playwright');const {spawn}=require('child_process');
const FPS=30, DUR=56, W=+process.argv[2], NW=+process.argv[3];
const total=FPS*DUR, per=Math.ceil(total/NW), a=W*per, b=Math.min(total,a+per);
(async()=>{
  const br=await chromium.launch(); const p=await br.newPage({viewport:{width:1080,height:1920}});
  p.on('pageerror',e=>console.log('ERR',e.message));
  await p.goto('file://'+__dirname+'/index.html'); await p.evaluate(()=>document.fonts.ready);
  const ff=spawn('ffmpeg',['-loglevel','error','-y','-f','image2pipe','-framerate',String(FPS),'-c:v','png','-i','-','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-profile:v','high','-r',String(FPS),`seg${W}.mp4`],{stdio:['pipe','inherit','inherit']});
  for(let f=a;f<b;f++){await p.evaluate(t=>render(t),f/FPS);const buf=await p.screenshot({type:'png'});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(f%100===0)console.log('w'+W,f);}
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await br.close(); console.log('done',W);
})();
