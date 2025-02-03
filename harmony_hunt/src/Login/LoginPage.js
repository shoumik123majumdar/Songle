import logo from './harmony-hunt-logo_480.png';
import './login_page.css';
import LoginButton from './LoginButton'

function LoginPage(){
    return (
        <div className="App">
            <div className="content-wrapper">
                <div className="title-area">
                    <header className="App-header">
                        <h1>Songle</h1>
                    </header>
                    {/*<img src={logo} alt="Logo" className="App-logo" />*/}
                </div>
                <LoginButton />
            </div>
        </div>
    );
}

export default LoginPage;