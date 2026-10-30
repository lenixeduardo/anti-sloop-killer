import Image from 'next/image';
export default function Safe(){return <><Image alt="Imagem da equipe" src="/team.png" width={200} height={80}/>
<a href="/about">Sobre</a><button onClick={() => console.log('ok')}>Funcional</button>
<iframe src="/video" title="Vídeo do produto" />
</>}

