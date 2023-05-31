<?php
class MyClass {
    public $global_array = array();
}
if (isset($argv[1])) {
    $id_folio = intval($argv[1]);   
}
$ruta_carpeta_html = '/home/serverholos/Licy'.'/';
if (!isset($id_folio)) {
    $response = array(
        'estatus' => 0,
        'texto' => 'El campo de id_folio está vacío, favor de verificar',
        'parametros' => ''
    );
    http_response_code(400);
    echo json_encode($response);
    return false;
}

if (!preg_match('/^\d+(?:\.[05]0*)?$/', $id_folio)) {
    $response = array(
        'estatus' => 0,
        'texto' => 'id_folio inválido: ' . $id_folio,
        'parametros' => ''
    );
    http_response_code(400);
    echo json_encode($response);
    return false;
}
$folio_carpeta = str_pad($id_folio, 6, "0", STR_PAD_LEFT);
$ruta_carpeta ='results/'.$folio_carpeta;
if (!(file_exists($ruta_carpeta) && is_dir($ruta_carpeta))) {
    mkdir($ruta_carpeta, 0755, TRUE);
}
$nombre_archivo = $folio_carpeta . '_eventos.json';
$ruta_completa = $nombre_archivo;
if (file_exists($ruta_completa) && !is_dir($ruta_completa)) {
    $response = array(
        'estatus' => 0,
        'texto' => 'El archivo ' . $nombre_archivo . ' ya existe en esta ruta: ' . $ruta_completa,
        'parametros' => $ruta_completa
    );
    http_response_code(400);
    echo json_encode($response);
    return false;
}
require_once 'simple_html_dom.php';
$archivos = glob($ruta_carpeta_html . '*.html');
$data_result = array();
$obj = new MyClass();
foreach ($archivos as $archivo) {
    $obj->global_array[] = saveHTMLData($archivo);
}
if (empty($obj->global_array)) {
    $response = array(
        'estatus' => 0,
        'texto' => 'No se generó ningún evento ya que no se encontraron HTML en ' . $ruta_carpeta_html,
        'parametros' => $ruta_carpeta
    );
    http_response_code(400);
    echo json_encode($response);
    return false;
}
if (!file_put_contents($ruta_completa, json_encode($obj->global_array, JSON_UNESCAPED_UNICODE))) {
    $response = array(
        'estatus' => 0,
        'texto' => 'Error al generar y guardar el archivo JSON',
        'parametros' => ''
    );
    http_response_code(400);
    echo json_encode($response);
    return false;
}
$response = array(
    'estatus' => 1,
    'texto' => 'Archivo JSON generado y guardado exitosamente en ' . $ruta_completa,
    'parametros' => ''
);
http_response_code(200);
echo json_encode($response);


    function saveHTMLData($file){
        $obj = new MyClass();
        $array_lista = array('#txtNumeroDeConcurso', '#divJuntaAclaraciones', '#divVisitaSitio', '#divFechaRecepcionPropuestas', '.proyectoPleigo');
        $html = new simple_html_dom();
        $html->load_file($file);
        //--------------------OBTIENE EL ID_LICITACION --------------------------------//
        if ($res = $html->find($array_lista[0])) {
            $evento_licitacion_id = $res[0]->attr['value'];
            //--------------------SESION DE ACLARACIONES --------------------------------//
            $res = getDataById($html ,$array_lista[1],$evento_licitacion_id, array('evento_no_sesion', 'evento_fecha_alta', 'evento_fecha_baja', 'fecha_inicio_sesion', 'fecha_cierre_sesion'), array('evento_id_utc'));
            if($res){
                $obj->global_array[]=$res;
            }
            //-------------------- VIISTAS EN SITIO --------------------------------//
            $res = getDataById($html,$array_lista[2],$evento_licitacion_id, array('evento_fecha_alta', 'evento_lugar')); // --------- Fecha Inicio , Lugar
            if($res){
                $obj->global_array[]=$res;
            }
            //-------------------- PRESENTACION DE OFERTAS --------------------------------//
            $res = getDataById($html,$array_lista[3],$evento_licitacion_id, array('evento_fecha_alta', 'evento_fecha_baja', 'archivo_de_financiamiento')); // --------- Fecha Inicio , Lugar
            if($res){
                $obj->global_array[]=$res;
            }
            //-------------------- OBTIENE APERTURA DE OFERTAS TECNICAS / ECONOMCAS / FALLO
            $res = getDataByClass($html,$array_lista[4],$evento_licitacion_id);
            if($res){
                $obj->global_array[]=$res;
            }
        }
        return $obj->global_array;
    }

    function getDataByClass($html,string $data,$evento_licitacion_id)
	{
        $data_result = array();
		if ($res = $html->find($data)) {
			foreach ($res as $item) {
				//filtra los que estan style:none / y quita los que no tienen id / quito a Anexos de Suspensión que no me sirve
				if (!isset($item->attr['style']) && !isset($item->attr['id']) && $item->find('td')) {
					$title = $item->find('b')[0]->nodes[0]->_[4];
					if (!($title=='Anexos de Apertura de Ofertas Técnicas' || $title=='Anexos de Apertura de Ofertas Ecónomicas' || $title=='Anexos de Fallo')){
						$insert['evento_licitacion_id'] = $evento_licitacion_id;
						$insert['evento_fecha_alta'] = validarData(trim(str_replace("hrs", "", $item->find('td')[1]->nodes[0]->_[4])), 'fecha');
						$insert['evento_fecha_baja'] = validarData(trim(str_replace("hrs", "", $item->find('td')[1]->nodes[0]->_[4])), 'fecha');
						$insert['evento_lugar'] = trim($item->find('td')[3]->nodes[0]->_[4]);
						//$data_result[] = $insert;
                        array_push($data_result, $insert);
					}
				}
			}
		}
        return $data_result;
	}

    function getDataById( $html,string $data, string $evento_licitacion_id, array $fields)
    {
        $data_result = array();
        if ($res = $html->find($data)[0]) {
            $count = 0;
            $title = $res->find('b')[0]->nodes[0]->_[4];
            $insert['evento_licitacion_id'] = $evento_licitacion_id;
            foreach ($res->find('td') as $item) {
                $dato = trim(str_replace("hrs", "", $item->nodes[0]->_[4]));
                if ($fields[$count] == 'evento_fecha_alta' || $fields[$count] == 'evento_fecha_baja' || $fields[$count] == 'fecha_inicio_sesion' || $fields[$count] == 'fecha_cierre_sesion') {
                    $dato = validarData($dato, 'fecha');
                }
                $insert[$fields[$count]] = $dato;
                $count == (count($fields) - 1) ? ($count = 0 & array_push($data_result, $insert)) : $count++;
            }
        }
        return $data_result;
    }


    function validarData($_var, $_type) {
        switch ($_type) {
            case 'int':
            case 'decimal':
                return is_numeric($_var);
            break;
            case 'fecha':
                $t = strlen($_var);
                if( $t <= 10 ) {
                    if(stripos($_var, "-")!== false ) {
                        $fecha = explode("-", $_var);
                    } else if( stripos($_var, "/")!== false ) {
                        $fecha = explode("/", $_var);
                    }
                    $valida = checkdate($fecha[1], $fecha[0], $fecha[2]);
                    if($valida) {
                        return $fecha[2]."-".$fecha[0]."-".$fecha[1];
                    } else {
                        return false;
                    }
                } else if( $t > 10 ) {
                    $fechaHora = explode(" ", $_var);
                    if(stripos($fechaHora[0], "-")!== false ) {
                        $fecha = explode("-", $fechaHora[0]);
                    } else if( stripos($fechaHora[0], "/")!== false ) {
                        $fecha = explode("/", $fechaHora[0]);
                    }
                    $valida = checkdate($fecha[1], $fecha[0], $fecha[2]);
                    $hora = explode(":", $fechaHora[1]);
                    if($hora[0] > 0 and $hora[0] < 24 ) {
                        if($hora[1] >= 0 and $hora[1] <= 59 ) {
                                $hora=$fechaHora[1];
                        } else {
                            $hora = false;
                        }
                    } else {
                        $hora = false;
                    }
                    if( $valida === true and $hora !== false ) {
                        return $fecha[2]."-".$fecha[1]."-".$fecha[0]." ".$hora;
                    } else {
                        return false;
                    }
                }
            break;
            case 'is_empty':
                return (strlen($_var)>0?false:true);
            break;
        }
    }

?>