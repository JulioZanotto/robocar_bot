#include <gz/plugin/Register.hh>
#include <gz/sim/System.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/components/Name.hh>
#include <gz/sim/components/ParentEntity.hh>
#include <gz/sim/components/Visual.hh>
#include <gz/sim/components/Pose.hh>
#include <gz/common/Console.hh> 
#include <vector>

using namespace gz;
using namespace sim;
using namespace systems;

class TrafficLightPlugin : public System, public ISystemConfigure, public ISystemPreUpdate
{
private:
    Model model_{kNullEntity};
    std::vector<Entity> reds_;
    std::vector<Entity> yellows_;
    std::vector<Entity> greens_;
    int current_state_{-1};
    bool initialized_{false};

    void SetActive(EntityComponentManager &_ecm, const std::vector<Entity>& entities, bool active)
    {
        for (const auto& entity : entities) {
            auto current_pose = _ecm.ComponentData<components::Pose>(entity);
            if (!current_pose) continue;

            gz::math::Pose3d new_pose = current_pose.value();
            // X = 0.0305 (Para fora, visível). X = 0.015 (Escondida dentro da caixa preta)
            new_pose.Pos().X() = active ? 0.0305 : 0.015;
            
            _ecm.SetComponentData<components::Pose>(entity, new_pose);
            _ecm.SetChanged(entity, components::Pose::typeId);
        }
    }

public:
    void Configure(const Entity &_entity, const std::shared_ptr<const sdf::Element> &,
                   EntityComponentManager &, EventManager &) override
    {
        model_ = Model(_entity);
    }

    void PreUpdate(const UpdateInfo &_info, EntityComponentManager &_ecm) override
    {
        if (_info.paused) return; 

        if (!initialized_) {
            // Varre todas as entidades visuais para encontrar as lentes brilhantes de TODOS os semáforos
            _ecm.Each<components::Visual, components::Name, components::ParentEntity>(
                [&](const Entity &_entity, const components::Visual *, const components::Name *_name, const components::ParentEntity *) -> bool
                {
                    std::string name = _name->Data();
                    if (name.find("red_visual_on") != std::string::npos) reds_.push_back(_entity);
                    else if (name.find("yellow_visual_on") != std::string::npos) yellows_.push_back(_entity);
                    else if (name.find("green_visual_on") != std::string::npos) greens_.push_back(_entity);
                    return true; 
                });

            if (!reds_.empty() && !yellows_.empty() && !greens_.empty()) {
                initialized_ = true;
                gzerr << "[TrafficLightPlugin] Encontradas " << reds_.size() << " cabeças de semáforo. Iniciando!" << std::endl;
            } else {
                return; 
            }
        }

        auto time_sec = std::chrono::duration_cast<std::chrono::seconds>(_info.simTime).count();
        int cycle_time = time_sec % 30; 
        
        int new_state = 0;
        if (cycle_time < 10) new_state = 0;      
        else if (cycle_time < 20) new_state = 1; 
        else new_state = 2;                      

        if (new_state != current_state_) {
            current_state_ = new_state;
            
            SetActive(_ecm, reds_,   current_state_ == 0);
            SetActive(_ecm, greens_, current_state_ == 1);
            SetActive(_ecm, yellows_,current_state_ == 2);
        }
    }
};

GZ_ADD_PLUGIN(TrafficLightPlugin, System, ISystemConfigure, ISystemPreUpdate)
GZ_ADD_PLUGIN_ALIAS(TrafficLightPlugin, "traffic_light_sim::TrafficLightPlugin")